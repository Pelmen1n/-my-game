import pygame
from pygame import Surface
from typing import List, Dict, Tuple, Optional

from components.button import Button
from constants import Colors, Sounds
from sprites.player import Player
from views.game_view import GameView
from weapons.lightning_wand import LightningWand
from weapons.magic_wand import MagicWand
from weapons.pistol import Pistol
from weapons.knife import Knife
from weapons.ball_lightning_wand import BallLightningWand


class SelectPlayerView:
    """
    Экран выбора игрока, который появляется при старте, позволяя выбрать персонажа.
    """

    def __init__(self, game):
        """
        Инициализация экрана выбора игрока.

        Аргументы:
            game: Главный экземпляр игры
            game_view: Игровой экран, который был приостановлен
        """
        self.game = game
        self.screen_width, self.screen_height = game.screen.get_size()

        # Создать заголовок
        self.title_font = pygame.font.SysFont("Arial", 48)
        self.title_text = self.title_font.render("Выберите игрока", True, Colors.WHITE)
        self.title_rect = self.title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))

        # Создать подзаголовок
        self.subtitle_font = pygame.font.SysFont("Arial", 24)
        self.subtitle_text = self.subtitle_font.render("Какого игрока хочешь?", True, Colors.WHITE)
        self.subtitle_rect = self.subtitle_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4 + 60))

        # Создать кнопки для выбора игрока
        self.player_buttons = []
        button_width = 380
        button_height = 80
        button_x = (self.screen_width - button_width) // 2
        button_y_start = self.screen_height // 2 - 30
        button_spacing = 100

        slot = 0
        button_y = button_y_start + (slot - 1) * button_spacing
        button = Button(
            button_x, button_y, button_width, button_height,
            f"Толстый (пистолет +1 ур.)", lambda: self.select_fat(),
            bg_color=(50, 100, 50), hover_color=(70, 150, 70),
            game=self.game
        )
        self.player_buttons.append(button)

        slot += 1
        button_y = button_y_start + (slot - 1) * button_spacing
        button = Button(
            button_x, button_y, button_width, button_height,
            f"Маг (волшебные облака)", lambda: self.select_mage(),
            bg_color=(50, 100, 50), hover_color=(70, 150, 70),
            game=self.game
        )

        self.player_buttons.append(button)

        slot += 1
        button_y = button_y_start + (slot - 1) * button_spacing
        button = Button(
            button_x, button_y, button_width, button_height,
            f"Воин (нож ближнего боя)", lambda: self.select_warrior(),
            bg_color=(50, 100, 50), hover_color=(70, 150, 70),
            game=self.game
        )
        self.player_buttons.append(button)

        slot += 1
        button_y = button_y_start + (slot - 1) * button_spacing
        button = Button(
            button_x, button_y, button_width, button_height,
            f"Электромаг (шаровая молния)", lambda: self.select_electromage(),
            bg_color=(50, 100, 50), hover_color=(70, 150, 70),
            game=self.game
        )
        self.player_buttons.append(button)

    def update(self, dt: float, events: List[pygame.event.Event]) -> None:
        """
        Обновить экран выбора игрока.

        Аргументы:
            dt: Дельта времени с последнего обновления
            events: Список событий pygame
        """
        # Обновить кнопки
        for button in self.player_buttons:
            button.update(events)

    def render(self, surface: Surface) -> None:
        """
        Отобразить экран выбора игрока.

        Аргументы:
            surface: Поверхность Pygame для отображения
        """
        # Создать полупрозрачный оверлей
        overlay = Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(Colors.GRAY_50)
        surface.blit(overlay, (0, 0))

        # Нарисовать заголовок и подзаголовок
        surface.blit(self.title_text, self.title_rect)
        surface.blit(self.subtitle_text, self.subtitle_rect)

        # Нарисовать кнопки выбора игрока
        for button in self.player_buttons:
            button.render(surface)

    def get_player(self):
        player_x = self.screen_width // 2
        player_y = self.screen_height // 2

        return Player(player_x, player_y)

    def select_fat(self) -> None:
        player = self.get_player()
        player.speed = 4
        player.max_health = 150
        player.current_health = 150

        player.weapon_slots[1] = Pistol()
        player.weapon_slots[1].level_up()

        self.game.view_stack.pop()
        self.game.view_stack.append(GameView(self.game, player))

        #Sounds.MUSTARDD.play()



    def select_mage(self):
        player = self.get_player()
        player.speed = 5
        player.max_health = 100
        player.current_health = 100

        player.weapon_slots[1] = MagicWand()

        self.game.view_stack.pop()
        self.game.view_stack.append(GameView(self.game, player))

        #Sounds.MMMM.play()


    def select_warrior(self):
        player = self.get_player()
        player.speed = 6
        player.max_health = 120
        player.current_health = 120

        player.weapon_slots[1] = Knife()

        self.game.view_stack.pop()
        self.game.view_stack.append(GameView(self.game, player))

        #Sounds.METAL_PIPE.play()


    def select_electromage(self):
        player = self.get_player()
        player.speed = 5
        player.max_health = 110
        player.current_health = 110

        player.weapon_slots[1] = BallLightningWand()
        player.weapon_slots[2] = LightningWand()

        self.game.view_stack.pop()
        self.game.view_stack.append(GameView(self.game, player))

        #Sounds.RANDOM_WEAPON.play()