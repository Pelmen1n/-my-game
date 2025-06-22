import pygame
from typing import List, Tuple, Optional, Callable

from components.button import Button
from components.progress_bar import ProgressBar
from constants import Colors


class OptionsMenu:
    """
    Экран настроек игры.
    """
    def __init__(self, game):
        """
        Инициализация экрана настроек.

        Аргументы:
            game: Главный экземпляр игры
        """
        self.game = game
        self.screen_width, self.screen_height = game.screen.get_size()

        # Шрифт заголовка
        self.title_font = pygame.font.SysFont("Arial", 48)
        self.title_text = self.title_font.render("Настройки", True, Colors.WHITE)
        self.title_rect = self.title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))

        # Шрифт для подписей
        self.label_font = pygame.font.SysFont("Arial", 24)

        # Подпись для громкости музыки
        self.music_label = self.label_font.render("Громкость музыки", True, Colors.WHITE)
        self.music_label_rect = self.music_label.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 60)
        )

        # Подпись для громкости эффектов
        self.sfx_label = self.label_font.render("Громкость эффектов", True, Colors.WHITE)
        self.sfx_label_rect = self.sfx_label.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 20)
        )

        # Создать ползунки громкости
        slider_width = 400
        slider_height = 30
        slider_x = (self.screen_width - slider_width) // 2

        # Ползунок громкости музыки
        music_slider_y = self.screen_height // 2 - 30
        self.music_slider = ProgressBar(
            x=slider_x,
            y=music_slider_y,
            width=slider_width,
            height=slider_height,
            progress=self.game.music_volume,
            bg_color=Colors.GRAY_50,
            fill_color=Colors.GREEN_200,
            border_color=Colors.GRAY_100,
            show_text=True,
            text_color=Colors.WHITE,
            font_size=18
        )

        # Ползунок громкости эффектов
        sfx_slider_y = self.screen_height // 2 + 50
        self.sfx_slider = ProgressBar(
            x=slider_x,
            y=sfx_slider_y,
            width=slider_width,
            height=slider_height,
            progress=self.game.sfx_volume,
            bg_color=Colors.GRAY_50,
            fill_color=Colors.GREEN_200,
            border_color=Colors.GRAY_100,
            show_text=True,
            text_color=Colors.WHITE,
            font_size=18
        )

        # Кнопка "Назад"
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        back_y = self.screen_height // 2 + 120
        self.back_button = Button(
            button_x, back_y, button_width, button_height,
            "Назад", self.go_back,
            bg_color=Colors.GRAY_100, hover_color=Colors.GRAY_150,
            game=self.game
        )

        # Состояние мыши для перетаскивания ползунков
        self.dragging_music = False
        self.dragging_sfx = False

    def update(self, dt, events):
        """
        Обновить экран настроек.

        Аргументы:
            dt: Дельта времени с момента последнего обновления
            events: Список событий pygame
        """
        self.back_button.update(events)

        # Обработка событий мыши для ползунков
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        # Проверка нажатия и отпускания кнопки мыши
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Проверка, если клик по ползунку музыки
                if self.music_slider.rect.collidepoint(mouse_pos):
                    self.dragging_music = True
                # Проверка, если клик по ползунку эффектов
                elif self.sfx_slider.rect.collidepoint(mouse_pos):
                    self.dragging_sfx = True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_music = False
                self.dragging_sfx = False

        # Обновление ползунков, если они перетаскиваются
        if self.dragging_music:
            self.update_slider_value(self.music_slider, mouse_pos[0])
            self.game.music_volume = self.music_slider.progress
            # Обновить фактическую громкость музыки в игре
            pygame.mixer.music.set_volume(self.game.music_volume)

        if self.dragging_sfx:
            self.update_slider_value(self.sfx_slider, mouse_pos[0])
            self.game.sfx_volume = self.sfx_slider.progress
            # Примечание: Громкость эффектов будет применена при воспроизведении звуков

    def update_slider_value(self, slider, mouse_x):
        """
        Обновить значение ползунка в зависимости от позиции мыши.

        Аргументы:
            slider: Ползунок (ProgressBar), который нужно обновить
            mouse_x: Координата x мыши
        """
        # Вычислить относительное положение внутри ползунка
        relative_x = max(0, min(mouse_x - slider.rect.x, slider.rect.width))
        progress = relative_x / slider.rect.width
        slider.set_progress(progress)

    def render(self, surface):
        """
        Отобразить экран настроек.

        Аргументы:
            surface: Поверхность Pygame для отображения
        """
        # Нарисовать заголовок
        surface.blit(self.title_text, self.title_rect)

        # Нарисовать подписи
        surface.blit(self.music_label, self.music_label_rect)
        surface.blit(self.sfx_label, self.sfx_label_rect)

        # Нарисовать ползунки
        self.music_slider.render(surface)
        self.sfx_slider.render(surface)

        # Нарисовать кнопку "Назад"
        self.back_button.render(surface)

    def go_back(self):
        """
        Вернуться в предыдущее меню.
        """
        # Удалить это меню из стека представлений
        self.game.view_stack.pop()
