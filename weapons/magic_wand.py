import pygame
from pygame import Surface
from typing import List, Tuple, Optional
import math
import random

from constants import Colors, Sounds
from sprites.magic_cloud import MagicCloud
from weapons.weapon_base import WeaponBase


class MagicWand(WeaponBase):
    """
    Оружие "Волшебная палочка", которое выпускает большие облака магии, наносящие урон всем врагам в области и постепенно исчезающие.
    """
    def __init__(self):
        """
        Инициализация волшебной палочки.
        """
        # Атрибуты оружия
        self.name = "Magic Wand"
        self.cooldown = 1.0  # секунд между выстрелами (дольше, чем у пистолета)
        self.time_since_last_shot = 0.0
        self.cloud_speed = 5
        self.speed_decay = 2
        self.cloud_damage = 10  # урон в секунду
        self.cloud_radius = 100  # начальный радиус облака

        # Группа для управления облаками магии
        self.clouds = pygame.sprite.Group()

    def update(self, dt: float, player_pos: Tuple[int, int], enemies, all_sprites, camera_pos: Tuple[int, int]) -> None:
        """
        Обновить состояние волшебной палочки и её облаков.

        Аргументы:
            dt: Дельта времени с последнего обновления
            player_pos: Позиция игрока (x, y)
            enemies: Группа врагов
            all_sprites: Группа всех спрайтов
            camera_pos: Позиция камеры (camera_x, camera_y)
        """
        # Обновить кулдаун
        self.time_since_last_shot += dt

        # Обновить облака и проверить столкновения с врагами
        defeated_enemies = []
        for cloud in self.clouds:
            cloud.update(dt)

            # Нанести урон по области врагам
            cloud_defeated = cloud.apply_damage_to_enemies(enemies, camera_pos)
            defeated_enemies.extend(cloud_defeated)

        # Удалить побеждённых врагов
        for enemy in defeated_enemies:
            enemy.kill()

    def shoot(self, player_pos: Tuple[int, int], enemies, all_sprites, camera_pos: Tuple[int, int]) -> bool:
        """
        Выпустить облако магии в направлении курсора мыши, если кулдаун позволяет.

        Аргументы:
            player_pos: Позиция игрока (x, y)
            enemies: Группа врагов
            all_sprites: Группа всех спрайтов
            camera_pos: Позиция камеры (camera_x, camera_y)

        Возвращает:
            True, если облако было выпущено, иначе False
        """
        # Проверить кулдаун
        if self.time_since_last_shot < self.cooldown:
            return False

        #Sounds.MMMM.play()

        # Получить позицию мыши для определения направления
        mouse_pos = pygame.mouse.get_pos()

        # Вычислить направление от игрока к мыши
        dx = mouse_pos[0] - player_pos[0]
        dy = mouse_pos[1] - player_pos[1]
        direction = pygame.math.Vector2(dx, dy)

        # Нормализовать направление
        if direction.length() > 0:
            direction = direction.normalize()

        # Преобразовать экранную позицию игрока в мировые координаты
        cloud_world_x = player_pos[0] - camera_pos[0]
        cloud_world_y = player_pos[1] - camera_pos[1]

        # Создать облако магии
        cloud = MagicCloud(
            cloud_world_x,
            cloud_world_y,
            direction,
            self.cloud_speed,
            self.speed_decay,
            self.cloud_damage,
            self.cloud_radius
        )

        # Добавить облако в группы
        self.clouds.add(cloud)
        all_sprites.add(cloud)

        # Сбросить кулдаун
        self.time_since_last_shot = 0.0

        return True

    def render_bullets(self, surface: Surface, camera_pos: Tuple[int, int]) -> None:
        """
        Отобразить все облака магии.

        Аргументы:
            surface: Поверхность Pygame для отрисовки
            camera_pos: Позиция камеры (camera_x, camera_y)
        """
        for cloud in self.clouds:
            # Вычислить экранную позицию облака
            cloud_screen_x = cloud.rect.centerx + camera_pos[0]
            cloud_screen_y = cloud.rect.centery + camera_pos[1]

            # Отобразить облако
            cloud.render(surface, (cloud_screen_x, cloud_screen_y))

    def level_up(self):
        """
        Улучшить волшебную палочку, повышая её атрибуты.
        """
        # Уменьшить кулдаун (ускорить кастование)
        self.cooldown = max(0.2, self.cooldown * 0.9)

        # Увеличить урон облака
        self.cloud_damage += 5

        # Увеличить радиус облака
        self.cloud_radius += 10

        print(f"Волшебная палочка улучшена! Урон: {self.cloud_damage}, Радиус: {self.cloud_radius}, Кулдаун: {self.cooldown:.2f}s")
