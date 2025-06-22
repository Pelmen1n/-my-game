import random

import pygame
from pygame import Surface
from typing import List, Dict, Tuple, Optional

from components.button import Button
from constants import Colors, Sounds
from sprites.player import Player
from weapons.magic_wand import MagicWand
from weapons.pistol import Pistol
from weapons.knife import Knife
from weapons.ball_lightning_wand import BallLightningWand
from weapons.lightning_wand import LightningWand


class LevelUpView:
    """
    Экран повышения уровня, который появляется, когда игрок получает новый уровень, позволяя выбрать оружие для улучшения.
    """
    def __init__(self, game, game_view, player: Player):
        """
        Инициализация экрана повышения уровня.

        Аргументы:
            game: Главный экземпляр игры
            game_view: Игровой экран, который был приостановлен
        """
        self.game = game
        self.game_view = game_view
        self.player = game_view.player
        self.screen_width, self.screen_height = game.screen.get_size()

        # Создать заголовок
        self.title_font = pygame.font.SysFont("Arial", 48)
        self.title_text = self.title_font.render("Level Up!", True, Colors.WHITE)
        self.title_rect = self.title_text.get_rect(center=(self.screen_width // 2, 40))

        # Создать подзаголовок
        self.subtitle_font = pygame.font.SysFont("Arial", 24)
        self.subtitle_text = self.subtitle_font.render("Выберите оружие для улучшения:", True, Colors.WHITE)
        self.subtitle_rect = self.subtitle_text.get_rect(center=(self.screen_width // 2, 100))

        # Создать кнопки для оружия
        self.weapon_buttons = []
        button_width = 250
        button_height = 25
        button_x = (self.screen_width - button_width) // 2
        button_y_start = 160
        button_spacing = 30

        # Создать кнопку для каждого оружия, которое есть у игрока
        for slot, weapon in self.player.weapon_slots.items():
            if weapon:
                button_y = button_y_start + (slot - 1) * button_spacing
                weapon_name = weapon.name
                button = Button(
                    button_x, button_y, button_width, button_height,
                    f"Улучшить {weapon_name}", lambda w=weapon: self.level_up_weapon(w),
                    bg_color=(50, 100, 50), hover_color=(70, 150, 70),
                    game=self.game
                )
                self.weapon_buttons.append(button)

        slot = len(self.player.weapon_slots) + 1

        print(self.player.current_level % 2 == 0)
        if self.player.current_level % 2 == 0:
            button_y = button_y_start + (slot - 1) * button_spacing
            button = Button(
                button_x, button_y, button_width, button_height,
                f"Случайное оружие", lambda: self.select_random_weapon(),
                bg_color=(120, 50, 100), hover_color=(70, 150, 70),
                game=self.game
            )
            self.weapon_buttons.append(button)
            slot += 1

        button_y = button_y_start + (slot - 1) * button_spacing
        button = Button(
            button_x, button_y, button_width, button_height,
            f"Скорость +1", lambda: self.increase_speed(),
            bg_color=(50, 50, 100), hover_color=(70, 150, 70),
            game=self.game
        )
        self.weapon_buttons.append(button)

        slot += 1
        button_y = button_y_start + (slot - 1) * button_spacing
        button = Button(
            button_x, button_y, button_width, button_height,
            f"Макс. здоровье +20", lambda: self.increase_health(),
            bg_color=(100, 50, 50), hover_color=(70, 150, 70),
            game=self.game
        )

        self.weapon_buttons.append(button)

    def update(self, dt: float, events: List[pygame.event.Event]) -> None:
        """
        Обновить экран повышения уровня.

        Аргументы:
            dt: Дельта времени с последнего обновления
            events: Список событий pygame
        """
        # Обновить кнопки
        for button in self.weapon_buttons:
            button.update(events)

    def render(self, surface: Surface) -> None:
        """
        Отобразить экран повышения уровня.

        Аргументы:
            surface: Поверхность Pygame для отображения
        """
        # Сначала отобразить игровой экран в фоне
        self.game_view.render(surface)

        # Создать полупрозрачный оверлей
        overlay = Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Черный с 150 альфа
        surface.blit(overlay, (0, 0))

        # Нарисовать заголовок и подзаголовок
        surface.blit(self.title_text, self.title_rect)
        surface.blit(self.subtitle_text, self.subtitle_rect)

        # Нарисовать кнопки оружия
        for button in self.weapon_buttons:
            button.render(surface)

    def level_up_weapon(self, weapon) -> None:
        """
        Улучшить выбранное оружие и вернуться в игру.

        Аргументы:
            weapon: Оружие для улучшения
        """
        # Улучшить оружие
        weapon.level_up()

        # Удалить этот экран повышения уровня из стека представлений
        self.game.view_stack.pop()

        Sounds.UPGRADE_CLICKED.play()


    def increase_speed(self):
        self.player.increase_speed()

        self.game.view_stack.pop()

        Sounds.STATS_INCREASE.play()


    def increase_health(self):
        self.player.increase_health()

        self.game.view_stack.pop()

        Sounds.STATS_INCREASE.play()


    def select_random_weapon(self):
        all_weapons = [
            MagicWand(),
            Pistol(),
            Knife(),
            BallLightningWand(),
            LightningWand()
        ]

        weapon = random.choice(all_weapons)

        for i in range(self.player.current_level // 2):
            weapon.level_up()

        self.player.weapon_slots[len(self.player.weapon_slots) + 1] = weapon

        self.game.view_stack.pop()

        #Sounds.RANDOM_WEAPON.play()