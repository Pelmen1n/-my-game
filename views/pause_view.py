import pygame
from pygame import Surface
from typing import List, Dict, Tuple, Optional

from components.button import Button
from constants import Colors


class PauseView:
    """
    Экран паузы, который появляется при постановке игры на паузу.
    """
    def __init__(self, game, game_view):
        """
        Инициализация экрана паузы.

        Аргументы:
            game: Главный экземпляр игры
            game_view: Игровой экран, который был приостановлен
        """
        self.game = game
        self.game_view = game_view
        self.screen_width, self.screen_height = game.screen.get_size()
        
        # Создать кнопки
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        
        # Кнопка продолжения
        resume_y = self.screen_height // 2 - 60
        self.resume_button = Button(
            button_x, resume_y, button_width, button_height,
            "Продолжить", self.resume_game,
            bg_color=(50, 100, 50), hover_color=(70, 150, 70),
            game=self.game
        )
        
        # Кнопка настроек
        options_y = self.screen_height // 2
        self.options_button = Button(
            button_x, options_y, button_width, button_height,
            "Настройки", self.show_options,
            bg_color=(50, 50, 100), hover_color=(70, 70, 150),
            game=self.game
        )
        
        # Кнопка возврата в главное меню
        menu_y = self.screen_height // 2 + 60
        self.menu_button = Button(
            button_x, menu_y, button_width, button_height,
            "Главное меню", self.return_to_main_menu,
            bg_color=(100, 50, 50), hover_color=(150, 70, 70),
            game=self.game
        )
        
        # Шрифт заголовка
        self.title_font = pygame.font.SysFont("Arial", 48)
        self.title_text = self.title_font.render("Пауза", True, Colors.WHITE)
        self.title_rect = self.title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        
    def update(self, dt: float, events: List[pygame.event.Event]) -> None:
        """
        Обновить экран паузы.
        
        Аргументы:
            dt: Дельта времени с последнего обновления
            events: Список событий pygame
        """
        # Проверка нажатия клавиши ESC для продолжения игры
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.resume_game()
                    return
        
        # Обновить кнопки
        self.resume_button.update(events)
        self.options_button.update(events)
        self.menu_button.update(events)
        
    def render(self, surface: Surface) -> None:
        """
        Отобразить экран паузы.
        
        Аргументы:
            surface: Поверхность Pygame для отрисовки
        """
        # Сначала отобразить игровой экран в фоне
        self.game_view.render(surface)
        
        # Создать полупрозрачный оверлей
        overlay = Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Черный цвет с альфа-каналом 150
        surface.blit(overlay, (0, 0))
        
        # Нарисовать заголовок
        surface.blit(self.title_text, self.title_rect)
        
        # Нарисовать кнопки
        self.resume_button.render(surface)
        self.options_button.render(surface)
        self.menu_button.render(surface)
        
    def resume_game(self) -> None:
        """
        Продолжить игру.
        """
        # Удалить это меню паузы из стека представлений
        self.game.view_stack.pop()
        
    def show_options(self) -> None:
        """
        Показать меню настроек.
        """
        from views.options_menu import OptionsMenu
        self.game.view_stack.append(OptionsMenu(self.game))
        
    def return_to_main_menu(self) -> None:
        """
        Вернуться в главное меню.
        """
        # Удалить все представления, пока не останется главное меню
        while len(self.game.view_stack) > 1:
            self.game.view_stack.pop()
