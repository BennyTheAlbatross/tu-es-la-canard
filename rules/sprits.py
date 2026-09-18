import os
import pygame
# Constants
RULES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(RULES_DIR)
ASSET_FOLDER = os.path.join(PROJECT_DIR, 'assets')
DUCK_SPEED = 5
TILE_SIZE = (40, 40)


def _first_existing(candidates):
    for filename in candidates:
        path = os.path.join(ASSET_FOLDER, filename)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f'None of these files were found: {candidates}')


def _make_black_transparent(surface):
    surface.set_colorkey((0, 0, 0))
    return surface

# finction to load sprits. one for each class duck, enemey, enviromental. 

def image_load_function(file_name):
    image = pygame.image.load(os.path.join(ASSET_FOLDER, file_name))
    image = pygame.transform.scale(image, TILE_SIZE)
    image.set_colorkey((0,0,0))
    return image


def _load_grid(file_name, columns, rows):
    """Split a generated sheet using rounded boundaries, then scale each cell."""
    # Assets are loaded before gameplay creates its display, so conversion here
    # would fail on a fresh launch. Generated sheets already contain alpha.
    sheet = pygame.image.load(os.path.join(ASSET_FOLDER, file_name))
    frames = []
    for row in range(rows):
        row_frames = []
        top = round(row * sheet.get_height() / rows)
        bottom = round((row + 1) * sheet.get_height() / rows)
        for column in range(columns):
            left = round(column * sheet.get_width() / columns)
            right = round((column + 1) * sheet.get_width() / columns)
            frame = sheet.subsurface((left, top, right - left, bottom - top)).copy()
            frame = pygame.transform.smoothscale(frame, TILE_SIZE)
            row_frames.append(frame)
        frames.append(row_frames)
    return frames

def load_duck_images():
    rows = _load_grid('generated/duck_animation_sheet.png', 4, 4)
    return {
        'front': rows[0],
        'back': rows[1],
        'right': rows[2],
        'left': [pygame.transform.flip(frame, True, False) for frame in rows[2]],
        'torch': rows[3],
    }

def load_enemy_images():
    enemy_fire = _load_grid('generated/enemy_fire_sheet.png', 4, 1)[0]
    enemy_water = _load_grid('generated/enemy_water_sheet.png', 4, 1)[0]

    rock_dir = os.path.join(ASSET_FOLDER, 'rock_enemy')
    #scale the images so they can be defined with ENEMY_SIZE

    def load_rock_frames(direction):
        frames = []
        for i in range(1, 6):
            frame = pygame.image.load(os.path.join(rock_dir, f'rock_{direction}_{i}.png'))
            frame = pygame.transform.scale(frame, TILE_SIZE)
            frame = _make_black_transparent(frame)
            frames.append(frame)
        return frames
    
    return {
        'enemy_fire': enemy_fire,
        'enemy_water': enemy_water,
        'enemy_rock': {
            'up': load_rock_frames('up'),
            'down': load_rock_frames('down'),
            'left': load_rock_frames('left'),
            'right': load_rock_frames('right'),
        }
    }

def load_enviromental_images():
    background_image = image_load_function('tile_dirt.png')
    border_image = image_load_function('tile_cave.png')
#    lava_tile = image_load_function('tile_lava.png')
    water_tile = image_load_function('tile_water.png')
    stone_tile = image_load_function('tile_stone.png')
    wood_tile = image_load_function('tile_wood.png')
    
    def load_lava_frames():
        frames = []
        for i in range(1, 5):
            frame = pygame.image.load(os.path.join(ASSET_FOLDER, f'lava_{i}.png'))
            frame = pygame.transform.scale(frame, TILE_SIZE)
            frame = _make_black_transparent(frame)
            frames.append(frame)
        return frames
    lava_frames = load_lava_frames()

    return {
        'background_image': background_image,
        'border_image': border_image,
        #'lava_tile': lava_tile,
        'water_tile': water_tile,
        'stone_tile': stone_tile,
        'wood_tile': wood_tile,
        'lava_tile': lava_frames,
        }

def load_object_images():
    gem_emeral = image_load_function('gem_green.png')
    gem_ruby = image_load_function('gem_red.png')
    gem_sapphire = image_load_function('gem_red.png')
    door_closed = image_load_function('doorClosed.png')
    door_open = image_load_function('doorOpen.png')

    return {
        'gem_emeral': gem_emeral,
        'gem_ruby': gem_ruby,
        'gem_sapphire': gem_sapphire,
        'door_closed': door_closed,
        'door_open': door_open,
        } 

def load_torch_images():
    # Load the 6-frame torch animation (red) as a list of tile-sized frames.
    torch_dir = os.path.join(ASSET_FOLDER, 'torch')
    frames = []
    for i in range(1, 7):
        frame = pygame.image.load(os.path.join(torch_dir, f'torch_red_{i}.png'))
        frame = pygame.transform.scale(frame, TILE_SIZE)
        frame = _make_black_transparent(frame)
        frames.append(frame)
    return {'torch': frames}

def load_collapsing_floor_images():
    return {
        'intact': image_load_function('collapsing_floor_intact.png'),
        'wobble': image_load_function('collapsing_floor_wobble.png'),
        'cracked': image_load_function('collapsing_floor_cracked.png'),
        'collapsed': image_load_function('collapsing_floor_collapsed.png'),
    }


def load_mechanic_images():
    rows = _load_grid('generated/gates_hidden_door_sheet.png', 3, 2)
    return {
        'one_way_up': rows[0][0],
        'one_way_right': rows[0][1],
        'one_way_down': rows[0][2],
        'one_way_left': rows[1][0],
        'hidden_door_closed': rows[1][1],
        'hidden_door_open': rows[1][2],
    }
