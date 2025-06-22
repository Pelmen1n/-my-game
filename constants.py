import pygame


pygame.mixer.init()

class Colors:
    WHITE = (255, 255, 255)
    GRAY_50 = (50, 50, 50)
    GRAY_100 = (100, 100, 100)
    GRAY_150 = (150, 150, 150)
    GRAY_200 = (200, 200, 200)
    GREEN_200 = (0, 200, 0)


class Sounds:
    CLICK = pygame.mixer.Sound('assets/sounds/click.wav')
    SHOOT = pygame.mixer.Sound('assets/sounds/Cards_Dart Goblin_blowdart_goblin_atk_02.ogg')
    GAME_OVER = pygame.mixer.Sound('assets/sounds/spongebob-fail.mp3')
    MENU_MUSIC = 'assets/sounds/Music_menu_03.ogg'
    BATTLE_MUSIC = 'assets/sounds/Music_2min_loop_battle_01.ogg'
    BACKGROUND_MUSIC = 'assets/sounds/Different Heaven, EH!DE - My Heart .mp3'
    DAMAGE_LIGHTNING = pygame.mixer.Sound('assets/sounds/roblox-death-sound_1.mp3')  # Повторное использование звука клика для урона
    DAMAGE_PLAYER = pygame.mixer.Sound('assets/sounds/aaah.mp3')
    KILL_1 = pygame.mixer.Sound('assets/sounds/om-nom-sad.mp3')
    MMMM = pygame.mixer.Sound('assets/sounds/levelup_sVAqjan.mp3')
    MUSTARDD = pygame.mixer.Sound('assets/sounds/mustardddddddd.mp3')
    LEVEL_UP = pygame.mixer.Sound('assets/sounds/apple-pay-sound.mp3')
    RANDOM_WEAPON = pygame.mixer.Sound('assets/sounds/let-me-know.mp3')
    UPGRADE_CLICKED = pygame.mixer.Sound('assets/sounds/discord-notification.mp3')
    METAL_PIPE = pygame.mixer.Sound('assets/sounds/metal-pipe-clang.mp3')
    STATS_INCREASE = pygame.mixer.Sound('assets/sounds/gay_CRD979V.mp3')
    RIZZ = pygame.mixer.Sound('assets/sounds/rizz-sounds.mp3')
