import pygame
from pygame import Surface, Rect
from typing import Callable, Optional, Tuple, List

from constants import Colors, Sounds


class Button:
    """
    Компонент кнопки для pygame, которую можно нажать для выполнения действия.
    """
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Callable,
        font_size: int = 24,
        text_color: Tuple[int, int, int] = Colors.WHITE,
        bg_color: Tuple[int, int, int] = Colors.GRAY_100,
        hover_color: Tuple[int, int, int] = Colors.GRAY_150,
        pressed_color: Tuple[int, int, int] = Colors.GRAY_50,
        border_radius: int = 5,
        sound_effect: Optional[pygame.mixer.Sound] = Sounds.CLICK,
        game = None
    ):
        """
        Инициализация новой кнопки.

        Аргументы:
            x: X-координата левого верхнего угла кнопки
            y: Y-координата левого верхнего угла кнопки
            width: Ширина кнопки
            height: Высота кнопки
            text: Текст на кнопке
            callback: Функция, вызываемая при нажатии на кнопку
            font_size: Размер шрифта текста кнопки
            text_color: RGB цвет текста
            bg_color: RGB цвет фона кнопки
            hover_color: RGB цвет кнопки при наведении
            pressed_color: RGB цвет кнопки при нажатии
            border_radius: Радиус скругления углов кнопки
            sound_effect: Звук, проигрываемый при нажатии
            game: Экземпляр главной игры для доступа к настройкам
        """
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.border_radius = border_radius
        self.sound_effect = sound_effect
        self.game = game

        # Состояние кнопки
        self.hovered = False
        self.pressed = False

        # Загрузка шрифта
        self.font = pygame.font.SysFont("Arial", font_size)
        self.text_surface = self.font.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update(self, events: List[pygame.event.Event]) -> None:
        """
        Обновить состояние кнопки на основе событий мыши.

        Аргументы:
            events: Список событий pygame для обработки
        """
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
                if self.hovered:
                    self.pressed = True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.pressed and self.hovered:
                    if self.sound_effect:
                        # Применить громкость SFX, если экземпляр игры доступен
                        if self.game:
                            self.sound_effect.set_volume(self.game.sfx_volume)
                        self.sound_effect.play()
                    self.callback()
                self.pressed = False

    def render(self, surface: Surface) -> None:
        """
        Отрисовать кнопку на переданной поверхности.

        Аргументы:
            surface: Поверхность pygame для отрисовки кнопки
        """
        # Определить цвет кнопки в зависимости от состояния
        if self.pressed:
            color = self.pressed_color
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.bg_color

        # Нарисовать кнопку
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)

        # Нарисовать текст
        surface.blit(self.text_surface, self.text_rect)

    def set_position(self, x: int, y: int) -> None:
        """
        Установить позицию кнопки.

        Аргументы:
            x: Новая X-координата левого верхнего угла кнопки
            y: Новая Y-координата левого верхнего угла кнопки
        """
        self.rect.x = x
        self.rect.y = y
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def set_text(self, text: str) -> None:
        """
        Установить текст кнопки.

        Аргументы:
            text: Новый текст для отображения на кнопке
        """
        self.text = text
        self.text_surface = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
