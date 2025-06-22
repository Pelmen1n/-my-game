import pygame
from pygame import mixer
from views.main_menu import MainMenu


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Свэг гейм 52 нгг")

        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.view_stack = []
        self.initialize_main_menu()

        # Инициализация микшера для звуков
        mixer.init()
        self.sfx_volume = 0.5
        self.music_volume = 0.5

        # Применить начальные настройки громкости
        pygame.mixer.music.set_volume(self.music_volume)

        # Данные игры, которые сохраняются между состояниями
        self.game_data = {
            "current_character": None,
            "upgrades": {
                "max_health": 0,
                "health_regen": 0,
                "damage": 0,
                "speed": 0,
                "cooldown_reduction": 0,
                "range": 0,
                "exp_multiplier": 0,
                "revive": 0
            },
            "gold": 0,
            "unlocked_difficulties": [1],  # Изначально доступна только первая сложность
            "current_difficulty": 1
        }

    def initialize_main_menu(self):
        # Начать с главного меню
        self.view_stack.append(MainMenu(self))

    def game_loop(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            if not self.view_stack:
                self.running = False
                continue
            # Обновляем и рендерим только верхнее состояние
            current_state = self.view_stack[-1]
            current_state.update(self.dt, events)
            self.screen.fill((0, 0, 0))
            current_state.render(self.screen)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.game_loop()
