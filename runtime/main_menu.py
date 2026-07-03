# setup python
import pygame, sys, os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)


import gameplay
from gameplay import screen_width, screen_height
from rules.sprits import TILE_SIZE, ASSET_FOLDER


MAPS_DIR = os.path.join(PROJECT_DIR, 'maps', 'game')


# setup pygame windows
pygame.init()
pygame.display.set_caption("tu es la canard")
screen = pygame.display.set_mode((screen_width, screen_height))

font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 64)


def draw_text(text, font, color, surface, x, y, center=False):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def list_maps():
    # Return (display_name, full_path) for every real .csv map, sorted.
    maps = []
    for name in sorted(os.listdir(MAPS_DIR)):
        if not name.lower().endswith('.csv'):
            continue
        if name.lower().endswith('.csv.txt'):
            continue
        display = os.path.splitext(name)[0]
        maps.append((display, os.path.join(MAPS_DIR, name)))
    return maps


def draw_menu(title, options, selected):
    screen.fill((0, 0, 0))
    screen.blit(
        pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_FOLDER, 'menu_background.png')),
            (screen_width, screen_height),
        ),
        (0, 0),
    )

    draw_text(title, title_font, (255, 0, 0), screen, screen_width // 2, 60, center=True)

    start_y = 140
    for i, option in enumerate(options):
        if i == selected:
            color = (255, 255, 0)
            label = "> " + option + " <"
        else:
            color = (255, 255, 255)
            label = option
        draw_text(label, font, color, screen, screen_width // 2, start_y + i * 40, center=True)

    pygame.display.update()


def death_screen(last_map):
    # Keyboard-centric death screen with Play Again / Main Menu.
    options = ["Play Again", "Main Menu"]
    selected = 0

    while True:
        screen.fill((0, 0, 0))
        screen.blit(
            pygame.transform.scale(
                pygame.image.load(os.path.join(ASSET_FOLDER, 'death_screen.png')),
                (screen_width, screen_height),
            ),
            (0, 0),
        )

        start_y = screen_height - 120
        for i, option in enumerate(options):
            if i == selected:
                color = (255, 255, 0)
                label = "> " + option + " <"
            else:
                color = (255, 255, 255)
                label = option
            draw_text(label, font, color, screen, screen_width // 2, start_y + i * 40, center=True)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if options[selected] == "Play Again":
                        launch_level(last_map)
                        selected = 0
                    else:
                        return


def launch_level(map_path):
    # Run the game and react to how it ended.
    global screen
    status = gameplay.main(map_path)
    # Restore the menu window/caption after gameplay took over the display.
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("tu es la canard")
    if status == 'dead':
        death_screen(map_path)
    # 'won' and 'quit' fall through back to the menu.


def main_menu():
    maps = list_maps()
    selected = 0

    while True:
        if maps:
            options = [name for name, _path in maps]
        else:
            options = ["(no maps found)"]

        draw_menu("tu es la canard", options, selected)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if maps:
                        _name, path = maps[selected]
                        launch_level(path)


main_menu()