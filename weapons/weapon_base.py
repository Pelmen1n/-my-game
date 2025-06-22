from abc import ABC

import pygame
from pygame import Surface
from typing import List, Tuple, Optional
import math

from constants import Colors
from sprites.bullet import Bullet


class WeaponBase(ABC):
    def update(self, dt: float, player_pos: Tuple[int, int], enemies, all_sprites, camera_pos: Tuple[int, int]) -> None:
        ...  # Обновить состояние оружия

    def shoot(self, player_pos: Tuple[int, int], enemies, all_sprites, camera_pos: Tuple[int, int]) -> bool:
        ...  # Выстрелить из оружия

    def render_bullets(self, surface: Surface, camera_pos: Tuple[int, int]) -> None:
        ...  # Отрисовать пули/снаряды

    def level_up(self):
        ...  # Улучшить оружие