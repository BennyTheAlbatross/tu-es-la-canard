import argparse
import csv
import os
from pathlib import Path

import pygame


PROJECT_DIR = Path(__file__).resolve().parent
MAPS_DIR = PROJECT_DIR / 'maps' / 'game'
OBJECTS_FILE = PROJECT_DIR / 'rules' / 'objects.csv'
ASSETS_DIR = PROJECT_DIR / 'assets'
WINDOW_SIZE = (1200, 760)
SIDEBAR_WIDTH = 300
TOPBAR_HEIGHT = 54
CELL_SIZE = 40
FPS = 60
PAINT_SELECTED = object()

PREVIEW_FILES = {
    'background': ['tile_dirt.png'],
    'border': ['tile_cave.png'],
    'lava': ['lava_1.png', 'lava_2.png', 'lava_3.png', 'lava_4.png'],
    'enemy_fire': ['enemy_fire.png'],
    'enemy_water': ['enemy_water.png'],
    'enemy_rock': ['rock_enemy/rock_down_1.png'],
    'gem_emerald': ['gem_green.png'],
    'gem_ruby': ['gem_red.png'],
    'gem_sapphire': ['gem_red.png'],
    'duck': ['duck_front.png'],
    'water': ['tile_water.png'],
    'stone': ['tile_stone.png'],
    'wood': ['tile_wood.png'],
    'end_door': ['doorClosed.png'],
    'torch': [f'torch/torch_red_{index}.png' for index in range(1, 7)],
    'collapsing_floor': [
        'collapsing_floor_intact.png',
        'collapsing_floor_wobble.png',
        'collapsing_floor_cracked.png',
        'collapsing_floor_collapsed.png',
    ],
}


def load_catalogue():
    with OBJECTS_FILE.open(encoding='utf-8-sig', newline='') as handle:
        return [row for row in csv.DictReader(handle)]


def load_previews(catalogue):
    previews = {}
    for item in catalogue:
        frames = []
        for relative_path in PREVIEW_FILES.get(item['object_name'], []):
            path = ASSETS_DIR / relative_path
            if not path.exists():
                continue
            image = pygame.image.load(path).convert_alpha()
            image.set_colorkey((0, 0, 0))
            frames.append(pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE)))
        if not frames:
            image = pygame.Surface((CELL_SIZE, CELL_SIZE))
            hue = int(item['object_number']) * 37
            image.fill((60 + hue % 150, 60 + hue * 2 % 150, 60 + hue * 3 % 150))
            frames.append(image)
        previews[int(item['object_number'])] = frames
    return previews


def read_map(path):
    rows = []
    with path.open(encoding='utf-8-sig', newline='') as handle:
        for raw_row in csv.reader(handle):
            row = []
            for cell in raw_row:
                value = cell.strip()
                row.append(int(value) if value else None)
            rows.append(row)
    width = max(len(row) for row in rows)
    return [row + [None] * (width - len(row)) for row in rows]


def write_map(path, grid):
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', encoding='utf-8', newline='') as handle:
        csv.writer(handle, lineterminator='\n').writerows(grid)
    os.replace(temporary, path)


class MapEditor:
    def __init__(self, map_path):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption('Tu es la canard — Map Editor')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 19)
        self.catalogue = load_catalogue()
        self.previews = load_previews(self.catalogue)
        self.map_paths = sorted(MAPS_DIR.glob('*.csv'))
        self.map_path = Path(map_path)
        self.grid = read_map(self.map_path)
        self.selected_index = 0
        self.cursor_column = 0
        self.cursor_row = 0
        self.camera_column = 0
        self.camera_row = 0
        self.palette_scroll = 0
        self.dirty = False
        self.message = ''
        self.message_time = 0.0
        self.command_mode = False
        self.command_text = ''
        self.show_help = True
        self.running = True
        self.held_direction = (0, 0)
        self.navigation_repeat_elapsed = 0.0
        self.navigation_repeat_started = False
        self.last_drag_cell = None

    @property
    def selected_id(self):
        return int(self.catalogue[self.selected_index]['object_number'])

    def visible_grid_size(self):
        width, height = self.screen.get_size()
        return (
            max(1, (width - SIDEBAR_WIDTH) // CELL_SIZE),
            max(1, (height - TOPBAR_HEIGHT) // CELL_SIZE),
        )

    def keep_cursor_visible(self):
        visible_columns, visible_rows = self.visible_grid_size()
        if self.cursor_column < self.camera_column:
            self.camera_column = self.cursor_column
        elif self.cursor_column >= self.camera_column + visible_columns:
            self.camera_column = self.cursor_column - visible_columns + 1
        if self.cursor_row < self.camera_row:
            self.camera_row = self.cursor_row
        elif self.cursor_row >= self.camera_row + visible_rows:
            self.camera_row = self.cursor_row - visible_rows + 1

    def ensure_size(self, column, row):
        changed = False
        while len(self.grid) <= row:
            self.grid.append([None] * len(self.grid[0]))
            changed = True
        if len(self.grid[0]) <= column:
            amount = column - len(self.grid[0]) + 1
            for grid_row in self.grid:
                grid_row.extend([None] * amount)
            changed = True
        if changed:
            self.dirty = True

    def move_cursor(self, column_change, row_change):
        target_column = max(0, self.cursor_column + column_change)
        target_row = max(0, self.cursor_row + row_change)
        self.ensure_size(target_column, target_row)
        self.cursor_column = target_column
        self.cursor_row = target_row
        self.keep_cursor_visible()

    def update_held_navigation(self, delta_seconds):
        if self.command_mode or self.show_help:
            self.held_direction = (0, 0)
            return

        keys = pygame.key.get_pressed()
        modifiers = pygame.key.get_mods()
        if modifiers & (pygame.KMOD_SHIFT | pygame.KMOD_CTRL):
            direction = (0, 0)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_h]:
            direction = (-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d] or keys[pygame.K_l]:
            direction = (1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_k]:
            direction = (0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_j]:
            direction = (0, 1)
        else:
            direction = (0, 0)

        if direction != self.held_direction:
            self.held_direction = direction
            self.navigation_repeat_elapsed = 0.0
            self.navigation_repeat_started = False
            if direction != (0, 0):
                self.move_cursor(*direction)
            return

        if direction == (0, 0):
            return

        self.navigation_repeat_elapsed += delta_seconds
        delay = 0.24 if not self.navigation_repeat_started else 0.055
        while self.navigation_repeat_elapsed >= delay:
            self.navigation_repeat_elapsed -= delay
            self.navigation_repeat_started = True
            self.move_cursor(*direction)
            delay = 0.055

    def pan(self, column_change, row_change):
        max_column = max(0, len(self.grid[0]) - 1)
        max_row = max(0, len(self.grid) - 1)
        self.camera_column = max(0, min(max_column, self.camera_column + column_change))
        self.camera_row = max(0, min(max_row, self.camera_row + row_change))

    def select(self, change):
        self.selected_index = (self.selected_index + change) % len(self.catalogue)

    def paint(self, column, row, object_id=PAINT_SELECTED):
        if column < 0 or row < 0:
            return
        self.ensure_size(column, row)
        value = self.selected_id if object_id is PAINT_SELECTED else object_id
        if self.grid[row][column] != value:
            self.grid[row][column] = value
            self.dirty = True

    def save(self):
        write_map(self.map_path, self.grid)
        self.dirty = False
        self.message = f'Saved {self.map_path.name}'
        self.message_time = 2.0

    def open_next_map(self):
        if self.dirty:
            self.message = 'Save with Ctrl+S before opening another map'
            self.message_time = 3.0
            return
        if not self.map_paths:
            return
        try:
            index = self.map_paths.index(self.map_path)
        except ValueError:
            index = -1
        self.map_path = self.map_paths[(index + 1) % len(self.map_paths)]
        self.grid = read_map(self.map_path)
        self.cursor_column = 0
        self.cursor_row = 0
        self.camera_column = 0
        self.camera_row = 0

    def execute_command(self):
        command = self.command_text.strip()
        self.command_mode = False
        self.command_text = ''
        if command == 'w':
            self.save()
        elif command == 'wq':
            self.save()
            self.running = False
        elif command == 'q!':
            self.running = False
        elif command == 'q':
            if self.dirty:
                self.message = 'Unsaved changes — use :wq or :q!'
                self.message_time = 3.0
            else:
                self.running = False
        elif command in ('e', 'next'):
            self.open_next_map()
        else:
            self.message = f'Unknown command: :{command}'
            self.message_time = 2.5

    def handle_command_key(self, event):
        if event.key == pygame.K_ESCAPE:
            self.command_mode = False
            self.command_text = ''
        elif event.key == pygame.K_RETURN:
            self.execute_command()
        elif event.key == pygame.K_BACKSPACE:
            self.command_text = self.command_text[:-1]
        elif event.unicode and event.unicode.isprintable():
            self.command_text += event.unicode

    def map_cell_at_mouse(self, position):
        x, y = position
        if x < SIDEBAR_WIDTH or y < TOPBAR_HEIGHT:
            return None
        column = self.camera_column + (x - SIDEBAR_WIDTH) // CELL_SIZE
        row = self.camera_row + (y - TOPBAR_HEIGHT) // CELL_SIZE
        return max(0, column), max(0, row)

    def handle_key(self, event):
        control = bool(event.mod & pygame.KMOD_CTRL)
        shift = bool(event.mod & pygame.KMOD_SHIFT)
        if control and event.key == pygame.K_s:
            self.save()
        elif event.key == pygame.K_COLON or (event.key == pygame.K_SEMICOLON and shift):
            self.command_mode = True
            self.command_text = ''
        elif event.key == pygame.K_QUESTION or (event.key == pygame.K_SLASH and shift):
            self.show_help = not self.show_help
        elif event.key == pygame.K_o:
            self.open_next_map()
        elif shift and event.key == pygame.K_h:
            self.pan(-5, 0)
        elif shift and event.key == pygame.K_l:
            self.pan(5, 0)
        elif shift and event.key == pygame.K_k:
            self.pan(0, -5)
        elif shift and event.key == pygame.K_j:
            self.pan(0, 5)
        elif control and event.key == pygame.K_u:
            self.pan(0, -max(1, self.visible_grid_size()[1] // 2))
        elif control and event.key == pygame.K_d:
            self.pan(0, max(1, self.visible_grid_size()[1] // 2))
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.paint(self.cursor_column, self.cursor_row)
        elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
            self.paint(self.cursor_column, self.cursor_row, None)
        elif event.key in (pygame.K_LEFTBRACKET, pygame.K_q):
            self.select(-1)
        elif event.key in (pygame.K_RIGHTBRACKET, pygame.K_e):
            self.select(1)

    def handle_mouse(self, event):
        if event.type == pygame.MOUSEWHEEL:
            mouse_x, _mouse_y = pygame.mouse.get_pos()
            if mouse_x < SIDEBAR_WIDTH:
                self.palette_scroll = max(0, self.palette_scroll - event.y * 34)
            elif event.x:
                self.pan(event.x * 3, 0)
            elif pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.pan(-event.y * 3, 0)
            else:
                self.pan(0, -event.y * 3)
            return
        if event.type == pygame.MOUSEBUTTONUP:
            self.last_drag_cell = None
            return
        if event.type == pygame.MOUSEMOTION:
            cell = self.map_cell_at_mouse(event.pos)
            if cell is None or cell == self.last_drag_cell:
                return
            if event.buttons[0]:
                self.cursor_column, self.cursor_row = cell
                self.paint(*cell)
                self.last_drag_cell = cell
            elif event.buttons[2]:
                self.cursor_column, self.cursor_row = cell
                self.paint(*cell, object_id=None)
                self.last_drag_cell = cell
            return
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        x, y = event.pos
        if x < SIDEBAR_WIDTH and y >= TOPBAR_HEIGHT:
            index = (y - TOPBAR_HEIGHT + self.palette_scroll) // 58
            if 0 <= index < len(self.catalogue):
                self.selected_index = index
            return
        cell = self.map_cell_at_mouse(event.pos)
        if cell:
            self.cursor_column, self.cursor_row = cell
            if event.button == 1:
                self.paint(*cell)
                self.last_drag_cell = cell
            elif event.button == 3:
                self.paint(*cell, object_id=None)
                self.last_drag_cell = cell

    def draw_topbar(self):
        width, _height = self.screen.get_size()
        pygame.draw.rect(self.screen, (28, 24, 30), (0, 0, width, TOPBAR_HEIGHT))
        marker = '*' if self.dirty else ''
        title = f'{self.map_path.name}{marker}  |  ?:help  : command  hjkl/arrows move  Enter paint  Delete blank'
        self.screen.blit(self.font.render(title, True, (240, 225, 205)), (14, 16))

    def draw_palette(self, animation_frame):
        _width, height = self.screen.get_size()
        pygame.draw.rect(self.screen, (35, 31, 38), (0, TOPBAR_HEIGHT, SIDEBAR_WIDTH, height))
        for index, item in enumerate(self.catalogue):
            y = TOPBAR_HEIGHT + index * 58 - self.palette_scroll
            if y + 58 < TOPBAR_HEIGHT or y > height:
                continue
            if index == self.selected_index:
                pygame.draw.rect(self.screen, (105, 76, 38), (4, y + 2, SIDEBAR_WIDTH - 8, 54), border_radius=5)
            object_id = int(item['object_number'])
            frames = self.previews[object_id]
            image = frames[animation_frame % len(frames)]
            self.screen.blit(image, (10, y + 8))
            label = f'{object_id}: {item["object_name"]}'
            detail = f'{item["object_type"]}  solid:{item["solid"]}'
            self.screen.blit(self.font.render(label, True, (245, 235, 215)), (60, y + 7))
            self.screen.blit(self.small_font.render(detail, True, (175, 165, 155)), (60, y + 32))

    def draw_grid(self, animation_frame):
        width, height = self.screen.get_size()
        pygame.draw.rect(
            self.screen,
            (15, 14, 17),
            (SIDEBAR_WIDTH, TOPBAR_HEIGHT, width - SIDEBAR_WIDTH, height - TOPBAR_HEIGHT),
        )
        visible_columns, visible_rows = self.visible_grid_size()
        for screen_row in range(visible_rows + 1):
            row = self.camera_row + screen_row
            if row >= len(self.grid):
                break
            for screen_column in range(visible_columns + 1):
                column = self.camera_column + screen_column
                if column >= len(self.grid[0]):
                    break
                x = SIDEBAR_WIDTH + screen_column * CELL_SIZE
                y = TOPBAR_HEIGHT + screen_row * CELL_SIZE
                object_id = self.grid[row][column]
                if object_id is None:
                    colour = (29, 27, 32) if (row + column) % 2 else (39, 36, 42)
                    pygame.draw.rect(self.screen, colour, (x, y, CELL_SIZE, CELL_SIZE))
                else:
                    frames = self.previews.get(object_id, self.previews[0])
                    image = frames[animation_frame % len(frames)]
                    self.screen.blit(image, (x, y))
                pygame.draw.rect(self.screen, (65, 61, 66), (x, y, CELL_SIZE, CELL_SIZE), 1)
                if object_id is not None:
                    number = self.small_font.render(str(object_id), True, (255, 255, 255))
                    number.set_alpha(190)
                    self.screen.blit(number, (x + 3, y + 2))

        cursor_x = SIDEBAR_WIDTH + (self.cursor_column - self.camera_column) * CELL_SIZE
        cursor_y = TOPBAR_HEIGHT + (self.cursor_row - self.camera_row) * CELL_SIZE
        pygame.draw.rect(self.screen, (255, 220, 55), (cursor_x, cursor_y, CELL_SIZE, CELL_SIZE), 3)

    def draw_help(self):
        if not self.show_help:
            return
        width, height = self.screen.get_size()
        overlay = pygame.Surface((min(690, width - 40), min(420, height - 90)), pygame.SRCALPHA)
        overlay.fill((17, 15, 20, 238))
        lines = [
            'MAP EDITOR CONTROLS  (? hides this overlay)',
            '',
            'h j k l / arrows / WASD   move cursor; grows map right or down',
            'Shift-H/J/K/L              pan viewport by five cells',
            'Ctrl-U / Ctrl-D            pan half a screen up / down',
            'Mouse wheel                scroll vertically; side-wheel pans sideways',
            'Shift + vertical wheel     alternate horizontal scrolling',
            'Q / E or [ / ]             choose previous / next catalogue item',
            'Enter / Space / left-drag  paint selected object continuously',
            'Delete / right-drag        make cells blank (not object 0)',
            'O or :e                    open next map',
            '',
            ':w save    :q quit    :wq save+quit    :q! discard+quit',
        ]
        for index, line in enumerate(lines):
            font = self.font if index == 0 else self.small_font
            colour = (255, 220, 80) if index == 0 else (235, 228, 215)
            overlay.blit(font.render(line, True, colour), (22, 18 + index * 28))
        self.screen.blit(overlay, ((width - overlay.get_width()) // 2, (height - overlay.get_height()) // 2))

    def draw_command_line(self):
        if not self.command_mode:
            return
        width, height = self.screen.get_size()
        pygame.draw.rect(self.screen, (12, 11, 14), (0, height - 38, width, 38))
        self.screen.blit(self.font.render(':' + self.command_text, True, (255, 245, 220)), (12, height - 30))

    def run(self):
        while self.running:
            delta_seconds = self.clock.tick(FPS) / 1000.0
            self.message_time = max(0.0, self.message_time - delta_seconds)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.dirty:
                        self.message = 'Unsaved changes — use :q! to discard'
                        self.message_time = 3.0
                    else:
                        self.running = False
                elif event.type == pygame.KEYDOWN:
                    if self.command_mode:
                        self.handle_command_key(event)
                    elif event.key == pygame.K_ESCAPE:
                        self.show_help = False
                    else:
                        self.handle_key(event)
                elif event.type in (
                    pygame.MOUSEBUTTONDOWN,
                    pygame.MOUSEBUTTONUP,
                    pygame.MOUSEMOTION,
                    pygame.MOUSEWHEEL,
                ):
                    self.handle_mouse(event)

            self.update_held_navigation(delta_seconds)

            animation_frame = int(pygame.time.get_ticks() / 180)
            self.draw_grid(animation_frame)
            self.draw_palette(animation_frame)
            self.draw_topbar()
            self.draw_help()
            self.draw_command_line()
            if self.message_time > 0:
                text = self.font.render(self.message, True, (255, 240, 90))
                self.screen.blit(text, (SIDEBAR_WIDTH + 12, TOPBAR_HEIGHT + 10))
            pygame.display.flip()
        pygame.quit()


def parse_args():
    parser = argparse.ArgumentParser(description='Edit Tu es la canard CSV maps')
    parser.add_argument('map', nargs='?', default=str(MAPS_DIR / 'map1.csv'))
    return parser.parse_args()


if __name__ == '__main__':
    arguments = parse_args()
    MapEditor(arguments.map).run()
