import pygame
from pygame import Surface
from typing import List, Tuple, Optional
import math

from constants import Colors, Sounds
from sprites.lightning import Lightning
from weapons.weapon_base import WeaponBase


class LightningWand(WeaponBase):
    """
    Оружие "Молния", которое выпускает 2 снаряда-молнии в двух врагов с наибольшим здоровьем.
    """
    def __init__(self):
        """
        Инициализация молнии.
        """
        # Атрибуты оружия
        self.name = "МОЛНИЯ"
        self.cooldown = 3.0  # секунд между выстрелами
        self.time_since_last_shot = 0.0
        self.lightning_speed = 15
        self.lightning_damage = 40
        self.num_projectiles = 2  # Количество выпускаемых снарядов

        # Группа для управления снарядами-молниями
        self.lightnings = pygame.sprite.Group()

    def update(self, dt: float, player_pos: Tuple[int, int], enemies, all_sprites, camera_pos: Tuple[int, int]) -> None:
        """
        Обновить состояние молнии и её снарядов.

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
        for lightning in self.lightnings:
            lightning.update(dt)

            # Проверить столкновения с врагами
            for enemy in enemies:
                # Создать временный rect для врага, соответствующий его позиции на экране
                enemy_collision_rect = enemy.rect.copy()
                enemy_collision_rect.x += camera_pos[0]
                enemy_collision_rect.y += camera_pos[1]

                # Создать временный rect для молнии, соответствующий её позиции на экране
                lightning_collision_rect = lightning.rect.copy()
                lightning_collision_rect.x += camera_pos[0]
                lightning_collision_rect.y += camera_pos[1]

                # Проверить столкновение с учётом смещённых rect
                if lightning_collision_rect.colliderect(enemy_collision_rect):
                    # Нанести урон врагу
                    if enemy.take_damage(lightning.damage):
                        # Враг повержен
                        enemy.kill()

                    # Удалить молнию
                    lightning.kill()
                    break

    def shoot(self, player_pos: Tuple[int, int], enemies, all_sprites, camera_pos: Tuple[int, int]) -> bool:
        """
        Выпустить 2 снаряда-молнии в двух врагов с наибольшим здоровьем, если кулдаун позволяет.

        Аргументы:
            player_pos: Позиция игрока (x, y)
            enemies: Группа врагов
            all_sprites: Группа всех спрайтов
            camera_pos: Позиция камеры (camera_x, camera_y)

        Возвращает:
            True, если снаряды-молнии были выпущены, False в противном случае
        """
        # Проверить кулдаун
        if self.time_since_last_shot < self.cooldown:
            return False

        # Если врагов нет, не стрелять
        if not enemies:
            return False

        # Отсортировать врагов по здоровью (высшее здоровье сначала)
        sorted_enemies = sorted(list(enemies), key=lambda e: e.current_health, reverse=True)

        # Выбрать N врагов с наибольшим здоровьем и циклически, если врагов мало
        target_enemies = []
        for i in range(self.num_projectiles):
            target_enemies.append(sorted_enemies[i % len(sorted_enemies)])

        # Если врагов недостаточно, не стрелять
        if len(target_enemies) < 1:
            return False

        # Флаг для отслеживания, был ли выпущен хотя бы один снаряд
        shot_fired = False

        # Стрелять в каждого целевого врага
        for target_enemy in target_enemies:
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

            # Преобразовать позицию игрока на экране в мировые координаты
            lightning_world_x = player_pos[0] - camera_pos[0]
            lightning_world_y = player_pos[1] - camera_pos[1]

            # Создать снаряд-молнию
            lightning = Lightning(
                lightning_world_x,
                lightning_world_y,
                direction,
                self.lightning_speed,
                self.lightning_damage
            )

            # Добавить молнию в группы
            self.lightnings.add(lightning)
            all_sprites.add(lightning)

            # Установить флаг, что мы выстрелили хотя бы одной молнией
            shot_fired = True

        # Сбросить кулдаун, если мы выстрелили хотя бы одной молнией
        if shot_fired:
            # Проиграть звук выстрела
            Sounds.RIZZ.play()

            self.time_since_last_shot = 0.0
            return True

        return False

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
        Улучшить молнию, повысив её атрибуты.
        """
        # Уменьшить кулдаун (ускорить кастование)
        self.cooldown = max(1.5, self.cooldown * 0.9)

        # Увеличить урон молнии
        self.lightning_damage += 6

        # Увеличить скорость молнии
        self.lightning_speed += 2

        self.num_projectiles += 1

        print(f"МОЛНИЯ leveled up! Снаряды: {self.num_projectiles}, Урон: {self.lightning_damage}, Скорость: {self.lightning_speed}, Кулдаун: {self.cooldown:.2f}s")
