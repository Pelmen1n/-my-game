import pygame
from pygame import Surface
from typing import List, Tuple, Optional
import math

from constants import Colors
from weapons.weapon_base import WeaponBase


class Knife(WeaponBase):
    """
    Оружие "Нож", которое поражает только врагов рядом с игроком.
    """
    def __init__(self):
        """
        Инициализация ножа.
        """
        # Атрибуты оружия
        self.name = "Knife"
        self.cooldown = 0.3  # секунд между ударами (быстрее, чем пистолет)
        self.time_since_last_shot = 0.0
        self.damage = 10
        self.range = 100  # Дальность в пикселях
        
        # Атрибуты анимации удара
        self.is_swinging = False
        self.swing_duration = 0.2  # секунд
        self.swing_time = 0.0
        self.swing_angle = 0  # Текущий угол удара
        
        # Визуальные атрибуты
        self.knife_length = 40
        self.knife_width = 10
        self.knife_color = (200, 200, 200)  # Серебряный цвет
        
        # Отслеживание врагов, поражённых текущим ударом, чтобы не поражать одного врага несколько раз
        self.enemies_hit = set()

    def update(self, dt: float, player_pos: Tuple[int, int], enemies, all_sprites, camera_pos: Tuple[int, int]) -> None:
        """
        Обновить состояние ножа.

        Аргументы:
            dt: Дельта времени с последнего обновления
            player_pos: Позиция игрока (x, y)
            enemies: Группа врагов
            all_sprites: Группа всех спрайтов
            camera_pos: Позиция камеры (camera_x, camera_y)
        """
        # Обновить кулдаун
        self.time_since_last_shot += dt
        
        # Обновить анимацию удара
        if self.is_swinging:
            self.swing_time += dt
            
            # Вычислить угол удара (от 0 до 180 градусов)
            progress = min(1.0, self.swing_time / self.swing_duration)
            self.swing_angle = 180 * progress
            
            # Проверить врагов в радиусе удара
            if progress < 1.0:  # Проверять только во время удара
                self.check_enemies_in_range(player_pos, enemies, camera_pos)
            
            # Завершить удар, когда время удара истечёт
            if self.swing_time >= self.swing_duration:
                self.is_swinging = False
                self.enemies_hit.clear()  # Очистить поражённых врагов для следующего удара

    def shoot(self, player_pos: Tuple[int, int], enemies, all_sprites, camera_pos: Tuple[int, int]) -> bool:
        """
        Ударить ножом, если кулдаун позволяет.

        Аргументы:
            player_pos: Позиция игрока (x, y)
            enemies: Группа врагов
            all_sprites: Группа всех спрайтов
            camera_pos: Позиция камеры (camera_x, camera_y)

        Возвращает:
            True, если нож был использован, False в противном случае
        """
        # Проверить кулдаун
        if self.time_since_last_shot < self.cooldown:
            return False
            
        # Начать анимацию удара
        self.is_swinging = True
        self.swing_time = 0.0
        self.swing_angle = 0
        self.enemies_hit.clear()
        
        # Проверить врагов в радиусе удара немедленно
        self.check_enemies_in_range(player_pos, enemies, camera_pos)
        
        # Сбросить кулдаун
        self.time_since_last_shot = 0.0
        
        return True
        
    def check_enemies_in_range(self, player_pos: Tuple[int, int], enemies, camera_pos: Tuple[int, int]) -> None:
        """
        Проверить врагов в радиусе действия ножа и нанести им урон.
        
        Аргументы:
            player_pos: Позиция игрока (x, y)
            enemies: Группа врагов
            camera_pos: Позиция камеры (camera_x, camera_y)
        """
        # Получить позицию мыши для направления удара
        mouse_pos = pygame.mouse.get_pos()
        
        # Вычислить направление от игрока к мыши
        dx = mouse_pos[0] - player_pos[0]
        dy = mouse_pos[1] - player_pos[1]
        direction = pygame.math.Vector2(dx, dy)
        
        # Нормализовать направление
        if direction.length() > 0:
            direction = direction.normalize()
            
        # Преобразовать позицию игрока на экране в мировые координаты
        player_world_x = player_pos[0] - camera_pos[0]
        player_world_y = player_pos[1] - camera_pos[1]
        
        # Проверить каждого врага
        for enemy in enemies:
            # Пропустить, если уже был поражён этим ударом
            if enemy in self.enemies_hit:
                continue
                
            # Вычислить позицию врага на экране
            enemy_screen_x = enemy.rect.centerx + camera_pos[0]
            enemy_screen_y = enemy.rect.centery + camera_pos[1]
            
            # Вычислить расстояние до врага
            dx = enemy_screen_x - player_pos[0]
            dy = enemy_screen_y - player_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Проверить, находится ли враг в радиусе действия
            if distance <= self.range:
                # Вычислить угол между направлением ножа и направлением к врагу
                enemy_direction = pygame.math.Vector2(dx, dy)
                if enemy_direction.length() > 0:
                    enemy_direction = enemy_direction.normalize()
                    
                # Вычислить скалярное произведение для определения, находится ли враг перед игроком
                dot_product = direction.dot(enemy_direction)
                
                # Если враг перед игроком (в пределах ~90 градусов от направления удара)
                if dot_product > 0:
                    # Нанести урон врагу
                    if enemy.take_damage(self.damage):
                        # Враг повержен
                        enemy.kill()
                    
                    # Отметить как поражённого, чтобы избежать повторного поражения за один удар
                    self.enemies_hit.add(enemy)

    def render_bullets(self, surface: Surface, camera_pos: Tuple[int, int]) -> None:
        """
        Отобразить анимацию удара ножом.

        Аргументы:
            surface: Поверхность Pygame для отрисовки
            camera_pos: Позиция камеры (camera_x, camera_y)
        """
        if not self.is_swinging:
            return
            
        # Получить позицию игрока на экране (центр экрана)
        player_screen_x = surface.get_width() // 2
        player_screen_y = surface.get_height() // 2
        
        # Получить позицию мыши для направления удара
        mouse_pos = pygame.mouse.get_pos()
        
        # Вычислить направление от игрока к мыши
        dx = mouse_pos[0] - player_screen_x
        dy = mouse_pos[1] - player_screen_y
        direction = pygame.math.Vector2(dx, dy)
        
        # Нормализовать направление
        if direction.length() > 0:
            direction = direction.normalize()
            
        # Вычислить базовый угол (угол направления мыши)
        base_angle = math.degrees(math.atan2(-direction.y, direction.x))
        
        # Вычислить смещение угла удара (-90 до +90 градусов)
        swing_offset = -90 + self.swing_angle
        
        # Вычислить окончательный угол
        angle = base_angle + swing_offset
        
        # Вычислить конечную точку ножа
        rad_angle = math.radians(angle)
        end_x = player_screen_x + math.cos(rad_angle) * self.knife_length
        end_y = player_screen_y - math.sin(rad_angle) * self.knife_length
        
        # Нарисовать линию ножа
        pygame.draw.line(
            surface,
            self.knife_color,
            (player_screen_x, player_screen_y),
            (end_x, end_y),
            self.knife_width
        )
        
        # Нарисовать рукоятку ножа
        handle_length = 10
        handle_angle = rad_angle + math.pi/2  # Перпендикулярно лезвию
        handle_x1 = player_screen_x + math.cos(handle_angle) * handle_length/2
        handle_y1 = player_screen_y - math.sin(handle_angle) * handle_length/2
        handle_x2 = player_screen_x - math.cos(handle_angle) * handle_length/2
        handle_y2 = player_screen_y + math.sin(handle_angle) * handle_length/2
        
        pygame.draw.line(
            surface,
            (139, 69, 19),  # Коричневый цвет для рукоятки
            (handle_x1, handle_y1),
            (handle_x2, handle_y2),
            self.knife_width
        )
        
        # Нарисовать кончик ножа (маленький круг)
        pygame.draw.circle(
            surface,
            self.knife_color,
            (int(end_x), int(end_y)),
            self.knife_width // 2
        )
        
        # Опционально, нарисовать индикатор радиуса действия во время удара
        # if self.swing_time < self.swing_duration * 0.5:  # Только в первой половине удара
        #     pygame.draw.circle(
        #         surface,
        #         (255, 255, 255, 50),  # Полу-прозрачный белый
        #         (player_screen_x, player_screen_y),
        #         self.range,
        #         1  # Толщина линии
        #     )

    def level_up(self):
        """
        Улучшить нож, повысив его атрибуты.
        """
        # Уменьшить кулдаун (ускорить удары)
        self.cooldown = max(0.1, self.cooldown * 0.9)
        
        # Увеличить урон
        self.damage += 10
        
        # Увеличить дальность
        self.range += 10
        
        print(f"Нож улучшен! Урон: {self.damage}, Дальность: {self.range}, Кулдаун: {self.cooldown:.2f}s")