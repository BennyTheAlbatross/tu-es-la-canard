import asyncio
# setup python
import pygame, sys, os, csv

# define current file paths

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

try:
    from . import gameplay
    from .gameplay import screen_width, screen_height
except ImportError:
    import gameplay
    from gameplay import screen_width, screen_height
from rules.sprits import TILE_SIZE, ASSET_FOLDER, load_torch_images
from rules import music as game_music
from rules import browser
import subprocess

MAPS_DIR = os.path.join(PROJECT_DIR, 'maps', 'game')

# setup pygame windows
pygame.init()
pygame.display.set_caption("tu es le canard")
screen = pygame.display.set_mode((screen_width, screen_height))
game_music.play()

font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 64)
torch_frames = load_torch_images()['torch']
_backgrounds = {}

def background(name):
    if name not in _backgrounds:
        _backgrounds[name] = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_FOLDER, name)), (screen_width, screen_height))
    return _backgrounds[name]


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
        full_path = os.path.join(MAPS_DIR, name)
        try:
            with open(full_path, encoding='utf-8-sig', newline='') as handle:
                has_spawn = any(cell.strip() == '9' for row in csv.reader(handle) for cell in row)
        except OSError:
            has_spawn = False
        if has_spawn:
            display = os.path.splitext(name)[0]
            maps.append((display, full_path))
    return maps


def draw_menu(title, options, selected, subtitle="", footer="Arrows/WASD: move    Enter: select    M: music    Esc: back"):
    screen.fill((0, 0, 0))
    screen.blit(
        background('menu_background.png'),
        (0, 0),
    )

    # Decorative torches for the main menu.
    torch_y = 92
    torch_frame = pygame.time.get_ticks() // 180 % len(torch_frames)
    left_torch = torch_frames[torch_frame]
    right_torch = pygame.transform.flip(left_torch, True, False)
    screen.blit(left_torch, (70, torch_y))
    screen.blit(right_torch, (screen_width - 70 - right_torch.get_width(), torch_y))

    draw_text(title, title_font, (255, 0, 0), screen, screen_width // 2, 60, center=True)

    if subtitle:
        draw_text(subtitle, pygame.font.Font(None, 25), (225, 205, 170), screen, screen_width // 2, 105, center=True)

    start_y = 130
    option_step = min(40, max(24, (screen_height - start_y - 34) // max(1, len(options))))
    for i, option in enumerate(options):
        if i == selected:
            color = (255, 255, 0)
            label = "> " + option + " <"
        else:
            color = (255, 255, 255)
            label = option
        draw_text(label, font, color, screen, screen_width // 2, start_y + i * option_step, center=True)

    if footer:
        draw_text(footer, pygame.font.Font(None, 20), (190, 190, 190), screen, screen_width // 2, screen_height - 15, center=True)
    pygame.display.update()


async def choose_menu(title, options, subtitle="", escape_result=None):
    # Retry here as well as at module startup: some desktop audio services are
    # not ready during the first few milliseconds of application launch.
    game_music.play()
    selected = 0
    clock = pygame.time.Clock()
    while True:
        await browser.next_frame(clock, 30)
        draw_menu(title, options, selected, subtitle)
        for event in browser.events():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return escape_result
            if event.key == pygame.K_m:
                game_music.toggle()
                continue
            if event.key in (pygame.K_UP, pygame.K_w):
                selected = (selected - 1) % len(options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                selected = (selected + 1) % len(options)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return selected


async def death_screen(last_map):
    # Keyboard-centric death screen with Play Again / Main Menu.
    options = ["Play Again", "Main Menu"]
    selected = 0
    clock = pygame.time.Clock()

    while True:
        await browser.next_frame(clock, 30)
        screen.fill((0, 0, 0))
        screen.blit(
            background('death_screen.png'),
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

        torch_y = 92
        torch_frame = pygame.time.get_ticks() // 180 % len(torch_frames)
        left_torch = torch_frames[torch_frame]
        right_torch = pygame.transform.flip(left_torch, True, False)
        screen.blit(left_torch, (70, torch_y))
        screen.blit(right_torch, (screen_width - 70 - right_torch.get_width(), torch_y))

        pygame.display.update()

        for event in browser.events():
            if event.type == pygame.QUIT:
                if browser.IS_WEB:
                    return "menu"
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if browser.IS_WEB:
                        return "menu"
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_m:
                    game_music.toggle()
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if options[selected] == "Play Again":
                        return 'play_again'
                    else:
                        return 'menu'


async def win_screen(last_map):
    # Keyboard-centric level-cleared screen with Play Again / Main Menu.
    options = ["Play Again", "Main Menu"]
    selected = 0
    clock = pygame.time.Clock()

    while True:
        await browser.next_frame(clock, 30)
        screen.fill((0, 0, 0))
        screen.blit(
            background('screen_cleared.png'),
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
            torch_y = 92
            torch_frame = pygame.time.get_ticks() // 90 % len(torch_frames)
            left_torch = torch_frames[torch_frame]
            right_torch = pygame.transform.flip(left_torch, True, False)
            screen.blit(left_torch, (70, torch_y))
            screen.blit(right_torch, (screen_width - 70 - right_torch.get_width(), torch_y))

            draw_text(label, font, color, screen, screen_width // 2, start_y + i * 40, center=True)

        pygame.display.update()

        for event in browser.events():
            if event.type == pygame.QUIT:
                if browser.IS_WEB:
                    return "menu"
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if browser.IS_WEB:
                        return "menu"
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_m:
                    game_music.toggle()
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if options[selected] == "Play Again":
                        return 'play_again'
                    else:
                        return 'menu'


async def launch_level(map_path):
    # Run the game and react to how it ended. Loop (never recurse) so repeated
    # plays don't stack menus/frames on the call stack.
    global screen
    while True:
        status = await gameplay.main_async(map_path)
        # Restore the menu window/caption after gameplay took over the display.
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("tu es le canard")
        if status == 'dead':
            if await death_screen(map_path) == 'play_again':
                continue
            return
        if status == 'won':
            if await win_screen(map_path) == 'play_again':
                continue
            return
        # 'quit' falls through back to the menu.
        return


def restore_menu_display():
    global screen
    pygame.event.set_grab(False)
    pygame.mouse.set_visible(True)
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("tu es le canard")


async def launch_raycaster(map_path):
    if browser.IS_WEB:
        from tuer_le_canard import tuer_le_canard
        status = await tuer_le_canard.main_async(map_path)
        restore_menu_display()
        return "quit" if status == "close" else None
    script = os.path.join(PROJECT_DIR, "tuer_le_canard", "tuer_le_canard.py")
    if pygame.mixer.get_init():
        pygame.mixer.music.pause()
    process = subprocess.Popen([sys.executable, script, os.path.abspath(map_path)])
    wait_clock = pygame.time.Clock()
    close_requested = False
    while process.poll() is None:
        # The ray-cast game owns the foreground window, but this parent window
        # must continue servicing its OS event queue or it is marked hung.
        for event in browser.events():
            if event.type == pygame.QUIT:
                close_requested = True
        pygame.event.pump()
        await browser.next_frame(wait_clock, 30)
    restore_menu_display()
    game_music.play()
    return "quit" if close_requested else None


def launch_map_editor():
    editor = os.path.join(PROJECT_DIR, "map_editor.py")
    subprocess.Popen([sys.executable, editor])


async def choose_level(maps):
    if not maps:
        await choose_menu("No levels found", ["Back"], "Add CSV files to maps/game", escape_result=None)
        return None
    result = await choose_menu(
        "Choose a level",
        [name for name, _path in maps] + ["Back"],
        "The same map can be played in either view",
        escape_result=None,
    )
    if result in (None, "quit") or result == len(maps):
        return result
    return maps[result]


async def choose_mode(level_name, map_path):
    while True:
        result = await choose_menu(
            "Choose a mode",
            (["2D dungeon", "Back"] if browser.is_touch_device() else ["2D dungeon", "Ray-cast dungeon", "Back"]),
            f"Level: {level_name}",
            escape_result=None,
        )
        if result in (None, "quit") or result == (1 if browser.is_touch_device() else 2):
            return result
        if result == 0:
            await launch_level(map_path)
            restore_menu_display()
        elif result == 1:
            if await launch_raycaster(map_path) == "quit":
                return "quit"


async def main_menu():
    restore_menu_display()
    game_music.play()
    maps = list_maps()
    while True:
        result = await choose_menu(
            "tu es le canard",
            (["Play"] if browser.IS_WEB else ["Play", "Map editor", "Quit"]),
            "A duck, a dungeon, and several bad decisions",
            escape_result=None if browser.IS_WEB else "quit",
        )
        if result == 2 or result == "quit":
            pygame.quit()
            return
        if result is None:
            continue
        if not browser.IS_WEB and result == 1:
            launch_map_editor()
            continue
        chosen = await choose_level(maps)
        if chosen == "quit":
            pygame.quit()
            return
        if chosen:
            mode_result = await choose_mode(*chosen)
            if mode_result == "quit":
                pygame.quit()
                return


if __name__ == "__main__":
    asyncio.run(main_menu())
