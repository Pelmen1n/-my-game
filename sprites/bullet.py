from typing import Tuple

import pygame
from pygame import Surface

from sprites.projectile_base import ProjectileBase


class Bullet(pygame.sprite.Sprite, ProjectileBase):
    """
    Спрайт пули, который движется по прямой и наносит урон врагам.
    """

    def __init__(self, x: int, y: int, direction: pygame.math.Vector2, speed: int = 10, damage: int = 10):
        """
        Инициализация пули.

        Аргументы:
            x: Начальная позиция x
            y: Начальная позиция y
            direction: Вектор направления (нормализованный)
            speed: Скорость движения в пикселях за кадр
            damage: Урон, наносимый врагам при столкновении
        """
        super().__init__()

        # Создать маленький спрайт пули (жёлтый круг)
        self.radius = 5
        self.image = Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 0), (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))

        # Атрибуты движения
        self.speed = speed
        self.direction = direction
        self.damage = damage

        # Точное положение пули (для точного движения)
        self.pos_x = float(x)
        self.pos_y = float(y)

        # Время жизни, чтобы пули не летели бесконечно
        self.lifetime = 2.0  # секунды
        self.time_alive = 0.0

    def update(self, dt: float) -> None:
        """
        Обновить позицию пули.

        Аргументы:
            dt: Дельта времени с последнего обновления
        """
        # Обновить позицию на основе направления и скорости
        self.pos_x += self.direction.x * self.speed
        self.pos_y += self.direction.y * self.speed

        # Обновить позицию rect
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

        # Обновить время жизни
        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.kill()  # Удалить пулю, когда время жизни истекает

    def render(self, surface: Surface, center_position: Tuple[int, int] = None) -> None:
        """
        Отобразить пулю на заданной поверхности.

        Аргументы:
            surface: Поверхность Pygame для отображения
            center_position: Необязательная кортеж (x, y), чтобы отобразить пулю в заданной позиции
        """
        if center_position is None:
            surface.blit(self.image, self.rect)
        else:
            # Создать временный rect для отображения в указанной позиции
            temp_rect = self.rect.copy()
            temp_rect.center = center_position
            surface.blit(self.image, temp_rect)
