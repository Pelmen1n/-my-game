import pygame
from pygame import Surface
from typing import Tuple
import math

from sprites.projectile_base import ProjectileBase


class Lightning(pygame.sprite.Sprite, ProjectileBase):
    """
    Спрайт молнии, который движется по прямой и наносит урон врагам.
    """

    def __init__(self, x: int, y: int, direction: pygame.math.Vector2, speed: int = 15, damage: int = 40):
        """
        Инициализация молнии.

        Аргументы:
            x: Начальная позиция x
            y: Начальная позиция y
            direction: Вектор направления (нормализованный)
            speed: Скорость движения в пикселях за кадр
            damage: Урон, наносимый врагам при столкновении
        """
        super().__init__()

        # Создать спрайт молнии (вытянутая синяя форма)
        self.width = 12
        self.height = 20
        self.image = Surface((self.width, self.height), pygame.SRCALPHA)

        # Нарисовать форму молнии
        lightning_color = (100, 150, 255)
        points = [
            (self.width // 2, 0),  # Верхняя точка
            (self.width, self.height // 3),  # Правая верхняя точка
            (self.width // 2 + 2, self.height // 2),  # Средняя правая точка
            (self.width, self.height),  # Правая нижняя точка
            (self.width // 2, self.height - self.height // 4),  # Нижняя средняя точка
            (0, self.height),  # Левая нижняя точка
            (self.width // 2 - 2, self.height // 2),  # Средняя левая точка
            (0, self.height // 3),  # Левая верхняя точка
        ]
        pygame.draw.polygon(self.image, lightning_color, points)

        # Добавить эффект свечения
        glow_surface = Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.polygon(glow_surface, (100, 150, 255, 100), points)
        self.image.blit(glow_surface, (0, 0))

        # Повернуть изображение по направлению движения
        angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=(x, y))

        # Атрибуты движения
        self.speed = speed
        self.direction = direction
        self.damage = damage

        # Отслеживание точного положения молнии (для точного движения)
        self.pos_x = float(x)
        self.pos_y = float(y)

        # Время жизни, чтобы предотвратить бесконечное движение молнии
        self.lifetime = 1.5  # секунды
        self.time_alive = 0.0

    def update(self, dt: float) -> None:
        """
        Обновить позицию молнии.

        Аргументы:
            dt: Дельта времени с момента последнего обновления
        """
        # Обновить позицию на основе направления и скорости
        self.pos_x += self.direction.x * self.speed
        self.pos_y += self.direction.y * self.speed

        # Обновить позицию прямоугольника
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

        # Обновить время жизни
        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.kill()  # Удалить молнию по истечении времени жизни

    def render(self, surface: Surface, center_position: Tuple[int, int] = None) -> None:
        """
        Отобразить молнию на заданной поверхности.

        Аргументы:
            surface: Поверхность Pygame для отображения
            center_position: Необязательная кортеж (x, y) для отображения молнии в заданной позиции
        """
        if center_position is None:
            surface.blit(self.image, self.rect)
        else:
            # Создать временный прямоугольник для отображения в указанной позиции
            temp_rect = self.rect.copy()
            temp_rect.center = center_position
            surface.blit(self.image, temp_rect)
