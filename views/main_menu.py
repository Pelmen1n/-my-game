import pygame
import time
from components.button import Button
from components.progress_bar import ProgressBar
from constants import Sounds


class MainMenu:
    """
    Главное меню игры.
    """
    def __init__(self, game):
        """
        Инициализация главного меню.

        Аргументы:
            game: Главный экземпляр игры
        """
        self.game = game
        self.screen_width, self.screen_height = game.screen.get_size()

        # Создать кнопки
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2

        # Кнопка начала игры
        start_y = self.screen_height // 2 - 60
        self.start_button = Button(
            button_x, start_y, button_width, button_height,
            "Начать игру", self.start_loading,
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

        # Кнопка выхода
        quit_y = self.screen_height // 2 + 60
        self.quit_button = Button(
            button_x, quit_y, button_width, button_height,
            "Выйти", self.quit_game,
            bg_color=(100, 50, 50), hover_color=(150, 70, 70),
            game=self.game
        )

        # Шрифт заголовка
        self.title_font = pygame.font.SysFont("Arial", 48)
        self.title_text = self.title_font.render("Супер крутая игра 2011 !!11!", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))

        # Создать прогресс-бар загрузки
        progress_bar_width = 400
        progress_bar_height = 30
        progress_bar_x = (self.screen_width - progress_bar_width) // 2
        progress_bar_y = self.screen_height - 100

        self.loading_progress_bar = ProgressBar(
            x=progress_bar_x,
            y=progress_bar_y,
            width=progress_bar_width,
            height=progress_bar_height,
            progress=0.0,
            bg_color=(30, 30, 30),
            fill_color=(0, 150, 255),
            border_color=(100, 100, 100),
            show_text=True,
            text_color=(255, 255, 255),
            font_size=18
        )

        # Переменные для симуляции загрузки
        self.loading = False
        self.loading_start_time = 0
        self.loading_duration = 0.7  # секунды

        # Воспроизвести музыку меню
        pygame.mixer.music.load(Sounds.MENU_MUSIC)
        pygame.mixer.music.play(-1)  # -1 означает бесконечный цикл

    def update(self, dt, events):
        """
        Обновить главное меню.

        Аргументы:
            dt: Дельта времени с последнего обновления
            events: Список событий pygame
        """
        self.start_button.update(events)
        self.options_button.update(events)
        self.quit_button.update(events)

        # Обновить прогресс-бар загрузки, если загрузка в процессе
        if self.loading:
            elapsed_time = time.time() - self.loading_start_time
            progress = min(elapsed_time / self.loading_duration, 1.0)
            self.loading_progress_bar.set_progress(progress)

            # Если загрузка завершена, начать игру
            if progress >= 1.0:
                self.start_game()
                self.loading = False

    def render(self, surface):
        """
        Отобразить главное меню.

        Аргументы:
            surface: Поверхность Pygame для отрисовки
        """
        # Нарисовать заголовок
        surface.blit(self.title_text, self.title_rect)

        # Нарисовать кнопки
        self.start_button.render(surface)
        self.options_button.render(surface)
        self.quit_button.render(surface)

        # Нарисовать прогресс-бар загрузки, если загрузка в процессе или завершена
        if self.loading or self.loading_progress_bar.progress > 0:
            self.loading_progress_bar.render(surface)

    def start_loading(self):
        """
        Начать симуляцию загрузки.
        """
        self.loading = True
        self.loading_start_time = time.time()
        self.loading_progress_bar.set_progress(0.0)
        print("Загрузка начата...")

    def start_game(self):
        """
        Начать игру.
        """
        print("Начало игры...")
        # Остановить музыку меню перед переходом к игровому представлению
        pygame.mixer.music.stop()

        # Переход к игровому представлению после загрузки
        from views.select_player_view import SelectPlayerView
        self.game.view_stack.append(SelectPlayerView(self.game))

    def show_options(self):
        """
        Показать меню настроек.
        """
        print("Показать настройки...")
        # Переход к меню настроек
        from views.options_menu import OptionsMenu
        self.game.view_stack.append(OptionsMenu(self.game))

    def quit_game(self):
        """
        Выйти из игры.
        """
        print("Выход из игры...")
        self.game.running = False
