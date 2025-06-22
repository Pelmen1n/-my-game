import pygame
from pygame import Surface
from typing import List, Dict, Tuple, Optional
from components.progress_bar import ProgressBar
from constants import Colors, Sounds
from weapons.weapon_base import WeaponBase


class Player(pygame.sprite.Sprite):
    """
    Спрайт игрока, которым можно управлять с помощью клавиш WASD.
    Имеет очки здоровья и слоты для оружия.
    """
    def __init__(self, x: int, y: int, speed: int = 5, max_health: int = 100):
        """
        Инициализация игрока.

        Аргументы:
            x: Начальная позиция x
            y: Начальная позиция y
            speed: Скорость движения в пикселях за кадр
            max_health: Максимальное количество очков здоровья
        """
        super().__init__()

        # Создать простой спрайт игрока (синий прямоугольник)
        self.width = 50
        self.height = 50
        self.image = Surface((self.width, self.height))
        self.image.fill((0, 0, 255))  # Синий цвет
        self.rect = self.image.get_rect(center=(x, y))

        # Атрибуты движения
        self.speed = speed
        self.direction = pygame.math.Vector2(0, 0)

        # Атрибуты здоровья
        self.max_health = max_health
        self.current_health = max_health

        self.score = 0
        self.current_level = 1
        self.score_multiplier = 100
        self.score_power = 1.1

        # Флаг, что игрок только что повысил уровень
        self.just_leveled_up = False

        # Создать полоску здоровья
        health_bar_width = 60
        health_bar_height = 10
        self.health_bar = ProgressBar(
            x=self.rect.x - (health_bar_width - self.width) // 2,
            y=self.rect.y - 20,
            width=health_bar_width,
            height=health_bar_height,
            progress=1.0,  # Полное здоровье
            bg_color=(50, 50, 50),
            fill_color=(0, 200, 0),  # Зелёный
            border_color=(200, 200, 200),
            show_text=False
        )
        self.score_bar = None
        self.score_bar_width = 100
        self.score_bar_height = 10
        self.reset_score_progress_bar()

        # Слоты для оружия
        self.weapon_slots: dict[int, Optional[WeaponBase]] = { }
        self.active_weapon_slot = 1

    def update(self, dt: float, events: List[pygame.event.Event], camera_pos=None) -> None:
        """
        Обновить состояние игрока и направление движения.

        Аргументы:
            dt: Дельта времени с последнего обновления
            events: Список событий pygame
            camera_pos: Необязательный кортеж (camera_x, camera_y) для обновления на основе движения игрока
        """
        # Обработка нажатий клавиш для движения
        keys = pygame.key.get_pressed()

        # Сброс направления
        self.direction.x = 0
        self.direction.y = 0

        # Движение WASD
        if keys[pygame.K_w]:
            self.direction.y = -1
        if keys[pygame.K_s]:
            self.direction.y = 1
        if keys[pygame.K_a]:
            self.direction.x = -1
        if keys[pygame.K_d]:
            self.direction.x = 1

        # Нормализовать диагональное движение
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        # Если camera_pos предоставлен, обновить его вместо позиции игрока
        if camera_pos is not None:
            camera_pos[0] -= self.direction.x * self.speed
            camera_pos[1] -= self.direction.y * self.speed

        # Обновить позицию полоски здоровья, чтобы она оставалась над игроком
        self.health_bar.set_position(
            self.rect.x - 5,  # Центрировать полоску здоровья над игроком
            self.rect.y - 15
        )

        # Обработка переключения слотов оружия
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.active_weapon_slot = 1
                elif event.key == pygame.K_2:
                    self.active_weapon_slot = 2
                elif event.key == pygame.K_3:
                    self.active_weapon_slot = 3

    def render(self, surface: Surface, center_position: Tuple[int, int] = None) -> None:
        """
        Отобразить игрока и полоску здоровья на заданной поверхности.

        Аргументы:
            surface: Поверхность Pygame для отображения
            center_position: Необязательный кортеж (x, y), чтобы отобразить игрока в определённой позиции
        """
        # Если center_position предоставлен, отобразить игрока в этой позиции
        # В противном случае использовать текущую позицию rect игрока
        if center_position:
            # Создать временной rect для отображения в центральной позиции
            temp_rect = self.rect.copy()
            temp_rect.center = center_position
            surface.blit(self.image, temp_rect)

            # Обновить позицию полоски здоровья, чтобы она была над игроком
            health_bar_x = temp_rect.x - 5
            health_bar_y = temp_rect.y - 15
            self.health_bar.set_position(health_bar_x, health_bar_y)
            self.health_bar.render(surface)

            score_bar_x = temp_rect.x - 25
            score_bar_y = temp_rect.y - 30
            self.score_bar.set_position(score_bar_x, score_bar_y)
            self.score_bar.render(surface)
        else:
            # Использовать текущую позицию игрока
            surface.blit(self.image, self.rect)
            self.health_bar.render(surface)
            self.score_bar.render(surface)

    def take_damage(self, amount: int) -> None:
        """
        Уменьшить здоровье игрока на заданное количество.

        Аргументы:
            amount: Количество урона
        """
        self.current_health = max(0, self.current_health - amount)
        self.health_bar.set_progress(self.current_health / self.max_health)

        # Проиграть звук урона
        Sounds.DAMAGE_PLAYER.play()

    def heal(self, amount: int) -> None:
        """
        Увеличить здоровье игрока на заданное количество.

        Аргументы:
            amount: Количество восстанавливаемого здоровья
        """
        self.current_health = min(self.max_health, self.current_health + amount)
        self.health_bar.set_progress(self.current_health / self.max_health)

        # Проиграть звук исцеления
        Sounds.MMMM.play()

    def add_score(self, amount: float) -> None:
        """
        Увеличить счёт игрока на заданное количество.
        """
        self.score += amount

        self.score_bar.set_progress(self.score / self.required_for_level_up())

        if self.required_for_level_up() < self.score:
            self.current_level += 1
            print("Повышение уровня! Текущий уровень: ", self.current_level)
            self.score = 0
            self.reset_score_progress_bar()

            # Проиграть звук повышения уровня
            Sounds.LEVEL_UP.play()

            # Установить флаг, чтобы указать, что игрок повысил уровень
            # Это будет проверяться в game_view для отображения level_up_view
            self.just_leveled_up = True

    def required_for_level_up(self):
        return self.score_multiplier * self.current_level ** self.score_power

    def reset_score_progress_bar(self):
        self.score_bar = ProgressBar(
            x=self.rect.x - (self.score_bar_width - self.width) // 2,
            y=self.rect.y - 35,
            width=self.score_bar_width,
            height=self.score_bar_height,
            progress=self.score / self.required_for_level_up(),  # Полное здоровье
            bg_color=(50, 50, 50),
            fill_color=(100, 100, 200),
            border_color=(200, 200, 200),
            show_text=False
        )

    def increase_speed(self) -> None:
        self.speed += 1

    def increase_health(self) -> None:
        self.current_health += 20
        self.max_health += 20
