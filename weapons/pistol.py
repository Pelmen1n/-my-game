import pygame
from pygame import Surface
from typing import List, Tuple, Optional
import math

from constants import Colors, Sounds
from sprites.bullet import Bullet
from weapons.weapon_base import WeaponBase


class Pistol(WeaponBase):
    """
    Оружие "Пистолет", которое стреляет пулями в ближайшего врага.
    """
    def __init__(self):
        """
        Инициализация пистолета.
        """
        # Атрибуты оружия
        self.name = "Pistol"
        self.cooldown = 0.5  # секунд между выстрелами
        self.time_since_last_shot = 0.0
        self.bullet_speed = 10
        self.bullet_damage = 10

        # Группа для управления пулями
        self.bullets = pygame.sprite.Group()

    def update(self, dt: float, player_pos: Tuple[int, int], enemies, all_sprites, camera_pos: Tuple[int, int]) -> None:
        """
        Обновить состояние пистолета и его пуль.

        Аргументы:
            dt: Дельта времени с последнего обновления
            player_pos: Позиция игрока (x, y)
            enemies: Группа врагов
            all_sprites: Группа всех спрайтов
            camera_pos: Позиция камеры (camera_x, camera_y)
        """
        # Обновить кулдаун
        self.time_since_last_shot += dt

        # Обновить пули
        for bullet in self.bullets:
            bullet.update(dt)

            # Проверить столкновения с врагами
            for enemy in enemies:
                # Создать временный rect для врага, соответствующий его позиции на экране
                enemy_collision_rect = enemy.rect.copy()
                enemy_collision_rect.x += camera_pos[0]
                enemy_collision_rect.y += camera_pos[1]

                # Создать временный rect для пули, соответствующий её позиции на экране
                bullet_collision_rect = bullet.rect.copy()
                bullet_collision_rect.x += camera_pos[0]
                bullet_collision_rect.y += camera_pos[1]

                # Проверить столкновение с учётом смещённых rect
                if bullet_collision_rect.colliderect(enemy_collision_rect):
                    # Нанести урон врагу
                    if enemy.take_damage(bullet.damage):
                        # Враг повержен
                        enemy.kill()

                    # Удалить пулю
                    bullet.kill()
                    break

    def shoot(self, player_pos: Tuple[int, int], enemies, all_sprites, camera_pos: Tuple[int, int]) -> bool:
        """
        Выстрелить пулей в ближайшего врага, если кулдаун позволяет.

        Аргументы:
            player_pos: Позиция игрока (x, y)
            enemies: Группа врагов
            all_sprites: Группа всех спрайтов
            camera_pos: Позиция камеры (camera_x, camera_y)

        Возвращает:
            True, если пуля была выпущена, иначе False
        """
        # Проверить кулдаун
        if self.time_since_last_shot < self.cooldown:
            return False

        # Найти ближайшего врага
        closest_enemy_rect = None
        closest_enemy = None
        closest_distance = float('inf')

        for enemy in enemies:
            if enemy.recently_targeted:
                continue

            # Вычислить позицию врага на экране
            enemy_screen_x = enemy.rect.centerx + camera_pos[0]
            enemy_screen_y = enemy.rect.centery + camera_pos[1]

            # Вычислить расстояние до игрока
            dx = enemy_screen_x - player_pos[0]
            dy = enemy_screen_y - player_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < closest_distance:
                closest_distance = distance
                closest_enemy_rect = (enemy_screen_x, enemy_screen_y)
                closest_enemy = enemy
        # Если врагов нет, не стрелять
        if closest_enemy_rect is None:
            return False

        closest_enemy.recently_targeted = True

        # Вычислить направление к ближайшему врагу
        dx = closest_enemy_rect[0] - player_pos[0]
        dy = closest_enemy_rect[1] - player_pos[1]
        direction = pygame.math.Vector2(dx, dy)

        # Нормализовать направление
        if direction.length() > 0:
            direction = direction.normalize()

        # Создать пулю
        # Преобразовать позицию игрока на экране в мировые координаты
        bullet_world_x = player_pos[0] - camera_pos[0]
        bullet_world_y = player_pos[1] - camera_pos[1]

        bullet = Bullet(
            bullet_world_x,
            bullet_world_y,
            direction,
            self.bullet_speed,
            self.bullet_damage
        )

        # Добавить пулю в группы
        self.bullets.add(bullet)
        all_sprites.add(bullet)

        # Проиграть звук выстрела
        Sounds.SHOOT.play()

        # Сбросить кулдаун
        self.time_since_last_shot = 0.0

        Sounds.SHOOT.play()

        return True

    def render_bullets(self, surface: Surface, camera_pos: Tuple[int, int]) -> None:
        """
        Отобразить все пули.

        Аргументы:
            surface: Поверхность Pygame для отрисовки
            camera_pos: Позиция камеры (camera_x, camera_y)
        """
        for bullet in self.bullets:
            # Вычислить позицию пули на экране
            bullet_screen_x = bullet.rect.centerx + camera_pos[0]
            bullet_screen_y = bullet.rect.centery + camera_pos[1]

            # Отобразить пулю
            bullet.render(surface, (bullet_screen_x, bullet_screen_y))

    def level_up(self):
        """
        Улучшить пистолет, повысив его атрибуты.
        """
        # Уменьшить кулдаун (увеличить скорость стрельбы)
        self.cooldown = max(0.1, self.cooldown * 0.9)

        # Увеличить урон пули
        self.bullet_damage += 5

        # Увеличить скорость пули
        self.bullet_speed += 2

        print(f"Пистолет улучшен! Урон: {self.bullet_damage}, Скорость: {self.bullet_speed}, Кулдаун: {self.cooldown:.2f}s")
