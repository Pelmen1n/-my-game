from abc import ABC
from typing import Tuple
from pygame import Surface


class ProjectileBase(ABC):
    def update(self, dt: float) -> None:
        ...

    def render(self, surface: Surface, center_position: Tuple[int, int] = None) -> None:
        ...