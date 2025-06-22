from typing import Tuple, List

import pygame
from pygame import Surface
import random

from constants import Sounds
from sprites.projectile_base import ProjectileBase


class MagicCloud(pygame.sprite.Sprite, ProjectileBase):
    """
    Спрайт магического облака, который наносит урон врагам в области и постепенно исчезает.
    """

    def __init__(self, x: int, y: int, direction: pygame.math.Vector2, speed: int = 5, speed_decay = 2, damage: int = 5, radius: int = 40):
        """
        Инициализация магического облака.

        Аргументы:
            x: Начальная позиция x
            y: Начальная позиция y
            direction: Вектор направления (нормализованный)
            speed: Скорость движения в пикселях за кадр
            damage: Урон, наносимый врагам в секунду
            radius: Начальный радиус облака
        """
        super().__init__()

        # Создать спрайт облака (синий/фиолетовый круг с прозрачностью)
        self.max_radius = radius
        self.current_radius = radius
        self.image = Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        
        # Нарисовать облако с помощью случайных частиц
        self.color = (100, 100, 255, 180)  # Синий с прозрачностью
        self.draw_cloud()
        
        self.rect = self.image.get_rect(center=(x, y))

        # Атрибуты движения
        self.speed = speed
        self.speed_decay = speed_decay
        self.direction = direction
        self.damage = damage
        self.damage_per_second = damage  # Оригинальный урон для расчёта затухания

        # Точное положение облака (для точного движения)
        self.pos_x = float(x)
        self.pos_y = float(y)

        # Время жизни и затухание
        self.max_lifetime = 3.0  # секунды
        self.time_alive = 0.0
        self.damage_interval = 0.1  # Наносить урон каждые N секунд
        self.time_since_last_damage = 0.0
        
        # Отслеживать врагов, которым был нанесён урон в текущем интервале
        self.damaged_enemies = set()

    def draw_cloud(self):
        """Нарисовать облако с помощью случайных частиц."""
        self.image.fill((0, 0, 0, 0))  # Очистить с прозрачностью
        
        # Нарисовать основное тело облака
        pygame.draw.circle(
            self.image, 
            self.color, 
            (self.max_radius, self.max_radius), 
            self.current_radius
        )
        
        # Добавить случайные мелкие частицы вокруг края для эффекта облака
        for _ in range(15):
            angle = random.uniform(0, 360)
            distance = random.uniform(0.7, 1.0) * self.current_radius
            x = self.max_radius + distance * pygame.math.Vector2.from_polar((1, angle))[0]
            y = self.max_radius + distance * pygame.math.Vector2.from_polar((1, angle))[1]
            
            particle_radius = random.uniform(0.2, 0.4) * self.current_radius
            particle_color = (
                self.color[0], 
                self.color[1], 
                self.color[2], 
                int(self.color[3] * random.uniform(0.7, 1.0))
            )
            
            pygame.draw.circle(
                self.image,
                particle_color,
                (int(x), int(y)),
                int(particle_radius)
            )

    def update(self, dt: float) -> None:
        """
        Обновить позицию, размер и урон магического облака.

        Аргументы:
            dt: Дельта времени с последнего обновления
        """

        self.speed -= self.speed_decay * dt
        if self.speed < 0:
            self.speed = 0.0
        # Обновить позицию на основе направления и скорости
        self.pos_x += self.direction.x * self.speed
        self.pos_y += self.direction.y * self.speed

        # Обновить позицию rect
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

        # Обновить время жизни и затухание
        self.time_alive += dt
        decay_factor = 1.0 - (self.time_alive / self.max_lifetime)
        
        if decay_factor <= 0:
            self.kill()  # Удалить облако по истечении времени жизни
            return
            
        # Обновить радиус и урон на основе затухания
        self.current_radius = int(self.max_radius * decay_factor)
        self.damage = self.damage_per_second * decay_factor
        
        # Заново нарисовать облако с новым радиусом
        self.draw_cloud()
        
        # Обновить интервал урона
        self.time_since_last_damage += dt

    def render(self, surface: Surface, center_position: Tuple[int, int] = None) -> None:
        """
        Отобразить магическое облако на заданной поверхности.

        Аргументы:
            surface: Поверхность Pygame для отображения
            center_position: Необязательная кортеж (x, y) для отображения облака в заданной позиции
        """
        if center_position is None:
            surface.blit(self.image, self.rect)
        else:
            # Создать временный rect для отображения в указанной позиции
            temp_rect = self.rect.copy()
            temp_rect.center = center_position
            surface.blit(self.image, temp_rect)
    
    def check_enemy_collision(self, enemy, camera_pos: Tuple[int, int]) -> bool:
        """
        Проверить, находится ли враг в области действия облака.
        
        Аргументы:
            enemy: Враг для проверки
            camera_pos: Позиция камеры (camera_x, camera_y)
            
        Возвращает:
            True, если враг находится в области действия облака, иначе False
        """
        # Вычислить расстояние между центром облака и центром врага
        cloud_screen_x = self.rect.centerx + camera_pos[0]
        cloud_screen_y = self.rect.centery + camera_pos[1]
        
        enemy_screen_x = enemy.rect.centerx + camera_pos[0]
        enemy_screen_y = enemy.rect.centery + camera_pos[1]
        
        dx = cloud_screen_x - enemy_screen_x
        dy = cloud_screen_y - enemy_screen_y
        distance = (dx * dx + dy * dy) ** 0.5
        
        # Проверить, находится ли враг в пределах текущего радиуса облака
        return distance <= self.current_radius + enemy.rect.width / 2
    
    def apply_damage_to_enemies(self, enemies, camera_pos: Tuple[int, int]) -> List:
        """
        Нанести урон всем врагам в области действия облака.
        
        Аргументы:
            enemies: Группа спрайтов врагов
            camera_pos: Позиция камеры (camera_x, camera_y)
            
        Возвращает:
            Список поверженных врагов
        """
        if self.time_since_last_damage < self.damage_interval:
            return []

        self.time_since_last_damage = 0.0
        self.damaged_enemies.clear()

        defeated_enemies = []
        
        for enemy in enemies:
            # Пропустить врагов, которым уже был нанесён урон в этом интервале
            if id(enemy) in self.damaged_enemies:
                continue
                
            if self.check_enemy_collision(enemy, camera_pos):
                # Нанести урон врагу
                if enemy.take_damage(int(self.damage)):
                    # Враг повержен
                    defeated_enemies.append(enemy)
                
                # Отметить этого врага как повреждённого в этом интервале
                self.damaged_enemies.add(id(enemy))

        return defeated_enemies
