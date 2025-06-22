import random

import pygame
from pygame import Surface
from typing import List, Tuple, Optional
from components.progress_bar import ProgressBar
from constants import Colors, Sounds
from sprites.player import Player


class Enemy(pygame.sprite.Sprite):
    """
    Спрайт врага с характеристиками здоровья и урона.
    """
    def __init__(self, player: Player, x: int, y: int, speed: int = 2, max_health: int = 50, damage: int = 10, color = (255, 0, 0)):
        """
        Инициализация врага.

        Аргументы:
            x: Начальная позиция x
            y: Начальная позиция y
            speed: Скорость движения в пикселях за кадр
            max_health: Максимальное количество очков здоровья
            damage: Урон, наносимый игроку при столкновении
        """
        super().__init__()

        self.player = player

        # Создать простой спрайт врага (красный прямоугольник)
        self.width = 40
        self.height = 40
        self.image = Surface((self.width, self.height))
        self.image.fill(color)  # Красный цвет
        self.rect = self.image.get_rect(center=(x, y))

        # Атрибуты движения
        self.speed = speed
        self.direction = pygame.math.Vector2(0, 0)

        # Боевая механика
        self.max_health = max_health
        self.current_health = max_health
        self.damage = damage
        self.recently_targeted = False

        # Создать полоску здоровья
        health_bar_width = 50
        health_bar_height = 8
        self.health_bar = ProgressBar(
            x=self.rect.x - (health_bar_width - self.width) // 2,
            y=self.rect.y - 15,
            width=health_bar_width,
            height=health_bar_height,
            progress=1.0,  # Полное здоровье
            bg_color=(50, 50, 50),
            fill_color=(200, 0, 0),  # Красный
            border_color=(200, 200, 200),
            show_text=False
        )

    def update(self, dt: float, player_pos: Tuple[int, int]) -> None:
        """
        Обновить позицию и состояние врага.

        Аргументы:
            dt: Дельта времени с момента последнего обновления
            player_pos: Позиция игрока (x, y)
        """
        # Двигаться к игроку
        player_x, player_y = player_pos

        # Вычислить вектор направления к игроку
        direction_x = player_x - self.rect.centerx
        direction_y = player_y - self.rect.centery

        # Создать нормализованный вектор направления
        direction = pygame.math.Vector2(direction_x, direction_y)
        if direction.length() > 0:
            direction = direction.normalize()

        # Двигаться к игроку
        self.rect.x += direction.x * self.speed
        self.rect.y += direction.y * self.speed

        # Обновить позицию полоски здоровья
        self.health_bar.set_position(
            self.rect.x - 5,  # Центрировать полоску здоровья над врагом
            self.rect.y - 15
        )

    def render(self, surface: Surface, center_position: Tuple[int, int] = None) -> None:
        """
        Отобразить врага и полоску здоровья на заданной поверхности.

        Аргументы:
            surface: Поверхность Pygame для отображения
            center_position: Необязательная кортеж (x, y) для отображения врага в заданной позиции
        """
        # Использовать текущую позицию rect, если center_position не задано
        if center_position is None:
            surface.blit(self.image, self.rect)
            self.health_bar.render(surface)
        else:
            # Создать временной rect для отображения в заданной позиции
            temp_rect = self.rect.copy()
            temp_rect.center = center_position
            surface.blit(self.image, temp_rect)

            # Обновить позицию полоски здоровья, чтобы она была над врагом в заданной позиции
            health_bar_x = temp_rect.x - 5
            health_bar_y = temp_rect.y - 15
            self.health_bar.set_position(health_bar_x, health_bar_y)
            self.health_bar.render(surface)

    def take_damage(self, amount: int) -> bool:
        """
        Уменьшить здоровье врага на заданное количество.

        Аргументы:
            amount: Количество урона

        Возвращает:
            True, если враг повержен (здоровье <= 0), иначе False
        """
        self.current_health = max(0, self.current_health - amount)
        self.health_bar.set_progress(self.current_health / self.max_health)

        return self.current_health <= 0

    def is_colliding_with_player(self, player_rect) -> bool:
        """
        Проверить, сталкивается ли враг с игроком.

        Аргументы:
            player_rect: Прямоугольник игрока

        Возвращает:
            True, если происходит столкновение, иначе False
        """
        return self.rect.colliderect(player_rect)

    def kill(self):
        self.player.add_score(self.max_health * 0.1 + self.damage * 0.3 + self.speed * 3)
        print("Добавление очков: ", self.max_health * 0.1 + self.damage * 0.3 + self.speed * 3, " игроку.")
        random.choice([Sounds.KILL_1]).play()
        super().kill()