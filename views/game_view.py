import pygame
from pygame import Surface
from typing import List, Dict, Tuple, Optional
import random

from sprites.player import Player
from sprites.enemy import Enemy
from components.button import Button
from constants import Colors, Sounds
from weapons.pistol import Pistol
from weapons.magic_wand import MagicWand
from weapons.knife import Knife


class GameView:
    """
    Игровой экран, содержащий игрока (управление WASD) и врагов.
    """
    def __init__(self, game, player: Player):
        """
        Инициализация игрового экрана.

        Аргументы:
            game: Главный экземпляр игры
        """
        self.game = game
        self.screen_width, self.screen_height = game.screen.get_size()

        # Создать игрока в центре экрана
        self.player = player

        # Создать группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Добавить игрока в группу спрайтов
        self.all_sprites.add(self.player)

        # Позиция камеры (мировые координаты)
        self.camera_x = 0
        self.camera_y = 0

        self.weapon_tick = 0

        # Создать начальных врагов
        self.spawn_enemies(5)

        self.dt_since_last_damage = 0
        self.player_damage_cooldown = 0.5

        # Состояние игры
        self.game_over = False
        self.score = 0
        self.music_stopped = False  # Флаг, отслеживающий, остановлена ли музыка

        # Элементы интерфейса
        self.font = pygame.font.SysFont("Arial", 24)

        # Воспроизвести фоновую музыку
        pygame.mixer.music.load(Sounds.BATTLE_MUSIC)
        pygame.mixer.music.play(-1)  # -1 означает зациклить бесконечно

    def spawn_enemies(self, count: int) -> None:
        """
        Создать указанное количество врагов в случайных позициях вокруг видимого экрана.

        Аргументы:
            count: Количество врагов для создания
        """
        for _ in range(count):
            # Спавн врагов в случайных позициях по краям видимого экрана
            side = random.randint(0, 3)

            # Вычислить позиции спавна относительно камеры
            # чтобы враги появлялись по краям видимого экрана
            if side == 0:  # Сверху
                x = random.randint(0, self.screen_width) - self.camera_x
                y = -50 - self.camera_y
            elif side == 1:  # Справа
                x = self.screen_width + 50 - self.camera_x
                y = random.randint(0, self.screen_height) - self.camera_y
            elif side == 2:  # Снизу
                x = random.randint(0, self.screen_width) - self.camera_x
                y = self.screen_height + 50 - self.camera_y
            else:  # Слева
                x = -50 - self.camera_x
                y = random.randint(0, self.screen_height) - self.camera_y


            red = min(self.player.current_level * 50, 255)
            green = max(255 - self.player.current_level * 20, 0)
            blue = random.randint(0, 50)
            enemy = Enemy(self.player, x, y,
                          speed=int(2 * (1 + self.player.current_level * 0.1)),
                          max_health=50 + self.player.current_level * 10,
                          damage=10 + self.player.current_level * 2,
                          color=(red, green, blue))
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def update(self, dt: float, events: List[pygame.event.Event]) -> None:
        """
        Обновить состояние игры.

        Аргументы:
            dt: Дельта времени с момента последнего обновления
            events: Список событий pygame
        """
        # Проверка нажатия клавиши паузы
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause_game()
                    return

        # Проверка, только что ли игрок получил уровень
        if hasattr(self.player, 'just_leveled_up') and self.player.just_leveled_up:
            self.player.just_leveled_up = False
            self.show_level_up_view()
            return

        # Обновить игрока и позицию камеры
        camera_pos = [self.camera_x, self.camera_y]
        self.player.update(dt, events, camera_pos)
        self.camera_x, self.camera_y = camera_pos

        # Обработка стрельбы оружием

        self.weapon_tick += 1
        self.weapon_tick %= len(self.player.weapon_slots)

        weapon = list(self.player.weapon_slots.values())[self.weapon_tick]

        if weapon:
            weapon.update(
                dt,
                (self.screen_width // 2, self.screen_height // 2),  # Игрок в центре экрана
                self.enemies,
                self.all_sprites,
                (self.camera_x, self.camera_y)
            )

            weapon.shoot(
                (self.screen_width // 2, self.screen_height // 2),  # Игрок в центре экрана
                self.enemies,
                self.all_sprites,
                (self.camera_x, self.camera_y)
            )

        # Обновить врагов
        for enemy in self.enemies:
            # Передать позицию игрока в мировых координатах
            enemy.update(dt, (self.screen_width // 2 - self.camera_x, self.screen_height // 2 - self.camera_y))

            # Создать временный прямоугольник для обнаружения столкновений в центре экрана
            player_collision_rect = self.player.rect.copy()
            player_collision_rect.center = (self.screen_width // 2, self.screen_height // 2)

            # Создать временный прямоугольник для врага, который соответствует его визуальной позиции на экране
            enemy_collision_rect = enemy.rect.copy()
            enemy_collision_rect.x += self.camera_x
            enemy_collision_rect.y += self.camera_y

            # print(player_collision_rect, enemy_collision_rect, enemy_collision_rect.colliderect(player_collision_rect))

            # Проверка на столкновения с игроком с использованием отрегулированного прямоугольника врага
            if (enemy_collision_rect.colliderect(player_collision_rect)
                    and self.dt_since_last_damage > self.player_damage_cooldown):
                print(f"Получение урона! {enemy.damage} {dt}")
                self.player.take_damage(enemy.damage)  # Масштабировать урон по времени
                self.dt_since_last_damage = 0

                # Проверка, не побежден ли игрок
                if self.player.current_health <= 0:
                    self.game_over = True
                    # Проиграть звук окончания игры
                    Sounds.GAME_OVER.play()

                    # Остановить боевую музыку, когда игра окончена (только один раз)
                    if not self.music_stopped:
                        pygame.mixer.music.stop()
                        self.music_stopped = True

        self.dt_since_last_damage += dt

        # Периодически спавнить новых врагов
        if random.random() < 0.01 + ((self.player.current_level - 1) * 0.005):  # 1% шанс за кадр
            self.spawn_enemies(1)

        # Обновляем прицел когда возвращаемся на первое оружие
        if self.weapon_tick == 0:
            for enemy in self.enemies:
                enemy.recently_targeted = False

    def render(self, surface: Surface) -> None:
        """
        Отрисовать игровой экран.

        Аргументы:
            surface: Поверхность Pygame для отрисовки
        """
        # Залить фон
        surface.fill((20, 20, 20))

        # Вычислить позицию игрока на экране (центр экрана)
        player_screen_x = self.screen_width // 2
        player_screen_y = self.screen_height // 2

        # Отрисовать все спрайты с учетом смещения камеры
        for sprite in self.all_sprites:
            if sprite == self.player:
                # Игрок всегда отрисовывается в центре экрана
                center_pos = (self.screen_width // 2, self.screen_height // 2)
                if hasattr(sprite, 'render'):
                    sprite.render(surface, center_pos)
                else:
                    # Создать временный прямоугольник для отрисовки в центре
                    temp_rect = sprite.rect.copy()
                    temp_rect.center = center_pos
                    surface.blit(sprite.image, temp_rect)
            else:
                # Применить смещение камеры к другим спрайтам
                sprite_screen_x = sprite.rect.x + self.camera_x
                sprite_screen_y = sprite.rect.y + self.camera_y

                if hasattr(sprite, 'render'):
                    # Передать позицию на экране в метод отрисовки
                    sprite.render(surface, (sprite_screen_x + sprite.rect.width // 2, 
                                           sprite_screen_y + sprite.rect.height // 2))
                else:
                    # Для спрайтов без пользовательского метода отрисовки
                    surface.blit(sprite.image, (sprite_screen_x, sprite_screen_y))

        # Отрисовать пули оружия
        for weapon in self.player.weapon_slots.values():
            # Пропустить оружие, которое не активно
            if not weapon:
                continue

            weapon.render_bullets(surface, (self.camera_x, self.camera_y))

        # Отрисовать интерфейс
        self.render_ui(surface)

        # Отрисовать экран окончания игры, если это необходимо
        if self.game_over:
            self.render_game_over(surface)

    def render_ui(self, surface: Surface) -> None:
        """
        Отрисовать интерфейс игры.

        Аргументы:
            surface: Поверхность Pygame для отрисовки
        """
        # Отрисовать текст здоровья
        health_text = self.font.render(f"Здоровье: {int(self.player.current_health)}/{self.player.max_health}", True, Colors.WHITE)
        surface.blit(health_text, (20, 20))

        # Отрисовать слоты оружия
        weapon_text = self.font.render("Оружие:", True, Colors.WHITE)
        surface.blit(weapon_text, (20, 50))

        for slot, weapon in self.player.weapon_slots.items():
            slot_color = Colors.GREEN_200 if slot == self.player.active_weapon_slot else Colors.GRAY_100
            weapon_name = "Пусто" if weapon is None else weapon.name
            slot_text = self.font.render(f"{slot}: {weapon_name}", True, slot_color)
            surface.blit(slot_text, (20, 50 + slot * 30))

    def render_game_over(self, surface: Surface) -> None:
        """
        Отрисовать экран окончания игры.

        Аргументы:
            surface: Поверхность Pygame для отрисовки
        """
        # Создать полупрозрачный оверлей
        overlay = Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Черный с 150 альфа-каналом
        surface.blit(overlay, (0, 0))

        # Текст окончания игры
        game_over_font = pygame.font.SysFont("Arial", 64)
        game_over_text = game_over_font.render("КОНЕЦ ИГРЫ", True, Colors.WHITE)
        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        surface.blit(game_over_text, game_over_rect)

        # Текст возврата в главное меню
        menu_font = pygame.font.SysFont("Arial", 32)
        menu_text = menu_font.render(f"Ваш уровень был {self.player.current_level}. \n" +
                                     "Нажмите ESC, чтобы вернуться в главное меню", True, Colors.WHITE)
        menu_rect = menu_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        surface.blit(menu_text, menu_rect)


    def pause_game(self) -> None:
        """
        Пауза игры и отображение меню паузы.
        """
        from views.pause_view import PauseView
        self.game.view_stack.append(PauseView(self.game, self))

    def show_level_up_view(self) -> None:
        """
        Показать экран повышения уровня, чтобы позволить игроку выбрать, какое оружие улучшить.
        """
        from views.level_up_view import LevelUpView
        self.game.view_stack.append(LevelUpView(self.game, self, self.player))
