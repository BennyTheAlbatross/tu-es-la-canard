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

def load_duck_images():
    duck_front = image_load_function('duck_front.png')
    duck_back = image_load_function('duck_back.png')
    duck_right = image_load_function('duck_walk_1.png')
    duck_left = image_load_function('duck_walk_2.png')  # this need to be inverted
    duck_left = pygame.transform.flip(duck_left, True, False)  # flip the left image horizontally

    return {
        'front': duck_front,
        'back': duck_back,
        'right': duck_right,
        'left': duck_left
    }

def load_enemy_images():
    enemy_fire = image_load_function('enemy_fire.png')
    enemy_water = image_load_function('enemy_water.png')

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
