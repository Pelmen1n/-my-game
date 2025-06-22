import pygame
from pygame import Surface
from typing import List, Tuple, Optional
import random
import math

from constants import Colors
from sprites.ball_lightning import BallLightning
from weapons.weapon_base import WeaponBase


class BallLightningWand(WeaponBase):
    """
    Оружие "Шаровая молния", которое выпускает снаряд-молнию в случайного врага,
    после чего молния отскакивает между врагами, нанося урон каждому поражённому врагу.
    """
    def __init__(self):
        """
        Инициализация шаровой молнии.
        """
        # Атрибуты оружия
        self.name = "ШАРОВАЯ МОЛНИЯ"
        self.cooldown = 1.4  # секунд между выстрелами
        self.time_since_last_shot = 0.0
        self.lightning_speed = 10
        self.lightning_damage = 40
        self.max_bounces = 5
        self.max_range = 800

        # Группа для управления снарядами-молниями
        self.lightnings = pygame.sprite.Group()

    def update(self, dt: float, player_pos: Tuple[int, int], enemies, all_sprites, camera_pos: Tuple[int, int]) -> None:
        """
        Обновить состояние шаровой молнии и её снарядов.

        Аргументы:
            dt: Дельта времени с последнего обновления
            player_pos: Позиция игрока (x, y)
            enemies: Группа врагов
            all_sprites: Группа всех спрайтов
            camera_pos: Позиция камеры (camera_x, camera_y)
        """
        # Обновить кулдаун
        self.time_since_last_shot += dt

        # Обновить молнии
        defeated_enemies = []
        for lightning in self.lightnings:
            # Обновить молнию
            lightning.update(dt)

            # Если у молнии нет текущей цели, попытаться найти новую
            if lightning.current_target is None:
                lightning.find_next_target(enemies, camera_pos)

            # Проверить, были ли враги побеждены этой молнией
            for enemy in enemies:
                if enemy.current_health <= 0 and id(enemy) in lightning.hit_enemies:
                    defeated_enemies.append(enemy)

        # Удалить побеждённых врагов
        for enemy in defeated_enemies:
            enemy.kill()

    def shoot(self, player_pos: Tuple[int, int], enemies, all_sprites, camera_pos: Tuple[int, int]) -> bool:
        """
        Выпустить снаряд-молнию в случайного врага, если кулдаун позволяет.

        Аргументы:
            player_pos: Позиция игрока (x, y)
            enemies: Группа врагов
            all_sprites: Группа всех спрайтов
            camera_pos: Позиция камеры (camera_x, camera_y)

        Возвращает:
            True, если снаряд-молния была выпущена, иначе False
        """
        # Проверить кулдаун
        if self.time_since_last_shot < self.cooldown:
            return False

        # Если врагов нет, не стрелять
        if not enemies:
            return False

        # Выбрать случайного врага в качестве начальной цели
        target_enemy = random.choice(list(enemies))

        # Вычислить позицию врага на экране
        enemy_screen_x = target_enemy.rect.centerx + camera_pos[0]
        enemy_screen_y = target_enemy.rect.centery + camera_pos[1]

        # Вычислить направление к целевому врагу
        dx = enemy_screen_x - player_pos[0]
        dy = enemy_screen_y - player_pos[1]
        direction = pygame.math.Vector2(dx, dy)

        # Нормализовать направление
        if direction.length() > 0:
            direction = direction.normalize()

        # Преобразовать позицию игрока в мировые координаты
        lightning_world_x = player_pos[0] - camera_pos[0]
        lightning_world_y = player_pos[1] - camera_pos[1]

        # Создать снаряд-молнию
        lightning = BallLightning(
            lightning_world_x,
            lightning_world_y,
            direction,
            self.lightning_speed,
            self.lightning_damage,
            self.max_bounces,
            self.max_range
        )

        # Добавить молнию в группы
        self.lightnings.add(lightning)
        all_sprites.add(lightning)

        # Сбросить кулдаун
        self.time_since_last_shot = 0.0

        return True

    def render_bullets(self, surface: Surface, camera_pos: Tuple[int, int]) -> None:
        """
        Отобразить все снаряды-молнии.

        Аргументы:
            surface: Поверхность Pygame для отрисовки
            camera_pos: Позиция камеры (camera_x, camera_y)
        """
        for lightning in self.lightnings:
            # Вычислить позицию молнии на экране
            lightning_screen_x = lightning.rect.centerx + camera_pos[0]
            lightning_screen_y = lightning.rect.centery + camera_pos[1]

            # Отобразить молнию
            lightning.render(surface, (lightning_screen_x, lightning_screen_y))

    def level_up(self):
        """
        Улучшить шаровую молнию, повысив её атрибуты.
        """
        # Уменьшить кулдаун (ускорить кастование)
        self.cooldown = max(0.7, self.cooldown * 0.9)

        # Увеличить урон молнии
        self.lightning_damage += 15

        # Увеличить количество отскоков
        self.max_bounces += 1

        print(f"ШАРОВАЯ МОЛНИЯ улучшена! Урон: {self.lightning_damage}, Отскоки: {self.max_bounces}, Кулдаун: {self.cooldown:.2f}s")
