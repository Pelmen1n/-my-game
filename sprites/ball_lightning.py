import pygame
from pygame import Surface
from typing import Tuple, List, Set
import random
import math

from constants import Sounds
from sprites.projectile_base import ProjectileBase


class BallLightning(pygame.sprite.Sprite, ProjectileBase):
    """
    Спрайт шаровой молнии, который отскакивает между врагами, нанося урон каждому поражённому врагу.
    """

    def __init__(self, x: int, y: int, direction: pygame.math.Vector2, speed: int = 10, damage: int = 60, max_bounces: int = 5, range: int = 800):
        """
        Инициализация шаровой молнии.

        Аргументы:
            x: Начальная позиция x
            y: Начальная позиция y
            direction: Вектор направления (нормализованный)
            speed: Скорость движения в пикселях за кадр
            damage: Урон, наносимый врагам при столкновении
            max_bounces: Максимальное количество отскоков до исчезновения
            range: Максимальная дистанция, которую может пройти снаряд
        """
        super().__init__()

        # Создать спрайт шаровой молнии (электрический синий круг с эффектом свечения)
        self.radius = 8
        self.image = Surface((self.radius * 2 + 4, self.radius * 2 + 4), pygame.SRCALPHA)

        # Нарисовать внешнее свечение
        pygame.draw.circle(self.image, (100, 150, 255, 100), (self.radius + 2, self.radius + 2), self.radius + 2)
        # Нарисовать внутреннее ядро
        pygame.draw.circle(self.image, (200, 230, 255, 230), (self.radius + 2, self.radius + 2), self.radius)

        self.rect = self.image.get_rect(center=(x, y))

        # Атрибуты движения
        self.speed = speed
        self.direction = direction
        self.damage = damage
        self.max_bounces = max_bounces
        self.bounces_left = max_bounces
        self.max_range = range
        self.distance_traveled = 0

        # Точное положение шаровой молнии (для точного движения)
        self.pos_x = float(x)
        self.pos_y = float(y)

        # Отслеживание цели
        self.current_target = None
        self.hit_enemies = set()  # Отслеживать поражённых врагов, чтобы не поражать одного врага дважды

        # Анимация и визуальные эффекты
        self.animation_frame = 0
        self.animation_speed = 0.2

    def update(self, dt: float) -> None:
        """
        Обновить положение и состояние шаровой молнии.

        Аргументы:
            dt: Дельта времени с момента последнего обновления
        """
        # Обновить анимацию
        self.animation_frame += dt * self.animation_speed
        if self.animation_frame >= 1:
            self.animation_frame = 0
            self._update_appearance()
        else:
            # Обеспечить обновление анимации, даже если animation_frame не достигает 1
            self._update_appearance()

        # Рассчитать движение на основе направления и скорости
        move_x = self.direction.x * self.speed
        move_y = self.direction.y * self.speed

        self.pos_x += move_x
        self.pos_y += move_y

        # Отслеживание пройденного расстояния
        self.distance_traveled += math.sqrt(move_x**2 + move_y**2)

        # Проверить, превысило ли расстояние максимальную дальность
        if self.distance_traveled >= self.max_range or self.bounces_left <= 0:
            self.kill()
            return

        # Если у нас есть текущая цель, проверьте, достигли ли мы её
        if self.current_target is not None:
            # Рассчитать расстояние до цели
            target_x = self.current_target.rect.centerx
            target_y = self.current_target.rect.centery
            dx = target_x - self.pos_x
            dy = target_y - self.pos_y
            distance_to_target = math.sqrt(dx * dx + dy * dy)

            # Если мы достаточно близки к цели, считайте, что она достигнута
            if distance_to_target < self.radius + self.current_target.rect.width / 2:
                # Обработать столкновение с целью
                self.handle_collision(self.current_target)

        # Обновить позицию rect
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

    def _update_appearance(self):
        """Обновить визуальный вид шаровой молнии для эффекта анимации."""
        # Очистить изображение
        self.image.fill((0, 0, 0, 0))

        # Немного рандомизировать свечение для электрического эффекта
        glow_radius = self.radius + 2 + random.uniform(-0.5, 0.5)
        core_radius = self.radius + random.uniform(-0.5, 0.5)

        # Нарисовать внешнее свечение с небольшим изменением цвета
        blue_var = random.randint(-20, 20)
        glow_color = (100, 150 + blue_var, 255, 100)
        pygame.draw.circle(self.image, glow_color, (self.radius + 2, self.radius + 2), glow_radius)

        # Нарисовать внутреннее ядро с небольшим изменением
        core_color = (200, 230, 255, 230)
        pygame.draw.circle(self.image, core_color, (self.radius + 2, self.radius + 2), core_radius)

    def render(self, surface: Surface, center_position: Tuple[int, int] = None) -> None:
        """
        Отобразить шаровую молнию на данном поверхности.

        Аргументы:
            surface: Поверхность Pygame для отображения
            center_position: Необязательная кортеж (x, y), чтобы отобразить шаровую молнию в определённой позиции
        """
        if center_position is None:
            surface.blit(self.image, self.rect)
        else:
            # Создать временный rect для отображения в указанной позиции
            temp_rect = self.rect.copy()
            temp_rect.center = center_position
            surface.blit(self.image, temp_rect)

    def find_next_target(self, enemies, camera_pos: Tuple[int, int], max_distance: float = 300) -> bool:
        """
        Найти следующего врага, к которому можно отскочить.

        Аргументы:
            enemies: Группа спрайтов врагов
            camera_pos: Позиция камеры (camera_x, camera_y)
            max_distance: Максимальное расстояние для поиска следующей цели

        Возвращает:
            True, если была найдена новая цель, иначе False
        """
        if self.bounces_left <= 0:
            return False

        closest_enemy = None
        closest_distance = max_distance

        for enemy in enemies:
            # Пропустить врагов, которые уже были поражены
            if id(enemy) in self.hit_enemies:
                continue

            # Рассчитать экранную позицию врага
            enemy_screen_x = enemy.rect.centerx + camera_pos[0]
            enemy_screen_y = enemy.rect.centery + camera_pos[1]

            # Рассчитать экранную позицию шаровой молнии
            lightning_screen_x = self.rect.centerx + camera_pos[0]
            lightning_screen_y = self.rect.centery + camera_pos[1]

            # Рассчитать расстояние
            dx = enemy_screen_x - lightning_screen_x
            dy = enemy_screen_y - lightning_screen_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < closest_distance:
                closest_distance = distance
                closest_enemy = enemy

        if closest_enemy:
            self.current_target = closest_enemy

            # Рассчитать направление к новой цели
            enemy_screen_x = closest_enemy.rect.centerx + camera_pos[0]
            enemy_screen_y = closest_enemy.rect.centery + camera_pos[1]
            lightning_screen_x = self.rect.centerx + camera_pos[0]
            lightning_screen_y = self.rect.centery + camera_pos[1]

            dx = enemy_screen_x - lightning_screen_x
            dy = enemy_screen_y - lightning_screen_y

            # Создать новый вектор направления
            self.direction = pygame.math.Vector2(dx, dy)
            if self.direction.length() > 0:
                self.direction = self.direction.normalize()

            return True

        return False

    def handle_collision(self, enemy) -> bool:
        """
        Обработать столкновение с врагом.

        Аргументы:
            enemy: Враг, который был поражён

        Возвращает:
            True, если враг был побеждён, иначе False
        """
        # Отметить этого врага как поражённого
        self.hit_enemies.add(id(enemy))

        # Нанести урон врагу
        defeated = enemy.take_damage(self.damage)

        # Уменьшить счётчик отскоков
        self.bounces_left -= 1

        # Очистить текущую цель
        self.current_target = None

        Sounds.DAMAGE_LIGHTNING.play()

        return defeated
