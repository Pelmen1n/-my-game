import pygame
from pygame import Surface, Rect
from typing import Tuple, Optional

from constants import Colors


class ProgressBar:
    """
    Компонент полосы прогресса для pygame, отображающий значение от 0 до 100%.
    """
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        progress: float = 0.0,
        bg_color: Tuple[int, int, int] = Colors.GRAY_50,
        fill_color: Tuple[int, int, int] = Colors.GREEN_200,
        border_color: Optional[Tuple[int, int, int]] = Colors.GRAY_100,
        border_width: int = 2,
        border_radius: int = 5,
        show_text: bool = True,
        text_color: Tuple[int, int, int] = Colors.WHITE,
        font_size: int = 16
    ):
        """
        Инициализация новой полосы прогресса.

        Аргументы:
            x: X-координата левого верхнего угла полосы прогресса
            y: Y-координата левого верхнего угла полосы прогресса
            width: Ширина полосы прогресса
            height: Высота полосы прогресса
            progress: Начальное значение прогресса (от 0.0 до 1.0)
            bg_color: RGB цвет фона
            fill_color: RGB цвет заполнения/прогресса
            border_color: RGB цвет рамки (None — без рамки)
            border_width: Толщина рамки в пикселях
            border_radius: Радиус скругления углов полосы
            show_text: Показывать ли текст с процентом
            text_color: RGB цвет текста
            font_size: Размер шрифта для текста процента
        """
        self.rect = Rect(x, y, width, height)
        self.progress = max(0.0, min(1.0, progress))  # Ограничить между 0 и 1
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.show_text = show_text
        self.text_color = text_color

        # Загрузить шрифт, если отображается текст
        if show_text:
            self.font = pygame.font.SysFont("Arial", font_size)
            self.update_text()

    def update_text(self) -> None:
        """
        Обновить поверхность текста с текущим процентом прогресса.
        """
        if self.show_text:
            percentage = int(self.progress * 100)
            self.text_surface = self.font.render(f"{percentage}%", True, self.text_color)
            self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def set_progress(self, progress: float) -> None:
        """
        Установить значение прогресса (от 0.0 до 1.0).

        Аргументы:
            progress: Новое значение прогресса от 0.0 до 1.0
        """
        self.progress = max(0.0, min(1.0, progress))  # Ограничить между 0 и 1
        if self.show_text:
            self.update_text()

    def render(self, surface: Surface) -> None:
        """
        Отрисовать полосу прогресса на переданной поверхности.

        Аргументы:
            surface: Поверхность pygame для отрисовки полосы прогресса
        """
        # Нарисовать фон
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)

        # Нарисовать заполнение прогресса
        if self.progress > 0:
            fill_rect = Rect(
                self.rect.x,
                self.rect.y,
                int(self.rect.width * self.progress),
                self.rect.height
            )
            # Убедиться, что заполнение учитывает скругление углов
            pygame.draw.rect(surface, self.fill_color, fill_rect, border_radius=self.border_radius)

        # Нарисовать рамку, если указана
        if self.border_color:
            pygame.draw.rect(
                surface,
                self.border_color,
                self.rect,
                width=self.border_width,
                border_radius=self.border_radius
            )

        # Нарисовать текст, если включено
        if self.show_text:
            surface.blit(self.text_surface, self.text_rect)

    def set_position(self, x: int, y: int) -> None:
        """
        Установить позицию полосы прогресса.

        Аргументы:
            x: Новая X-координата левого верхнего угла полосы прогресса
            y: Новая Y-координата левого верхнего угла полосы прогресса
        """
        self.rect.x = x
        self.rect.y = y
        if self.show_text:
            self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def set_colors(self, bg_color: Optional[Tuple[int, int, int]] = None, 
                  fill_color: Optional[Tuple[int, int, int]] = None,
                  border_color: Optional[Tuple[int, int, int]] = None,
                  text_color: Optional[Tuple[int, int, int]] = None) -> None:
        """
        Установить цвета полосы прогресса.

        Аргументы:
            bg_color: Новый цвет фона (RGB кортеж)
            fill_color: Новый цвет заполнения (RGB кортеж)
            border_color: Новый цвет рамки (RGB кортеж)
            text_color: Новый цвет текста (RGB кортеж)
        """
        if bg_color:
            self.bg_color = bg_color
        if fill_color:
            self.fill_color = fill_color
        if border_color:
            self.border_color = border_color
        if text_color and self.show_text:
            self.text_color = text_color
            self.update_text()
