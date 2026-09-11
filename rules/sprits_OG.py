
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

def load_duck_images():
    duck_front = pygame.image.load(os.path.join(ASSET_FOLDER, 'duck_front.png'))
    duck_back = pygame.image.load(os.path.join(ASSET_FOLDER, 'duck_back.png'))
    duck_right = pygame.image.load(os.path.join(ASSET_FOLDER, 'duck_walk_1.png'))
    duck_left = pygame.image.load(os.path.join(ASSET_FOLDER, 'duck_walk_2.png'))  # this need to be inverted
    duck_left = pygame.transform.flip(duck_left, True, False)  # Flip the image horizontally

    #scale the images so they can be defined with DUCK_SIZE
    duck_front = pygame.transform.scale(duck_front, TILE_SIZE)
    duck_back = pygame.transform.scale(duck_back, TILE_SIZE)
    duck_right = pygame.transform.scale(duck_right, TILE_SIZE)
    duck_left = pygame.transform.scale(duck_left, TILE_SIZE)

    duck_front.set_colorkey((0,0,0))  
    duck_back.set_colorkey((0,0,0)) 
    duck_right.set_colorkey((0,0,0))
    duck_left.set_colorkey((0,0,0))

    return {
        'front': duck_front,
        'back': duck_back,
        'right': duck_right,
        'left': duck_left
    }

def load_enemy_images():
    enemy_fire = pygame.image.load(os.path.join(ASSET_FOLDER, 'enemy_fire.png'))
    enemy_water = pygame.image.load(os.path.join(ASSET_FOLDER, 'enemy_water.png'))
    rock_dir = os.path.join(ASSET_FOLDER, 'rock_enemy')
    #scale the images so they can be defined with ENEMY_SIZE
    enemy_fire = pygame.transform.scale(enemy_fire, TILE_SIZE)
    enemy_water = pygame.transform.scale(enemy_water, TILE_SIZE)

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
    background_image = pygame.image.load(os.path.join(ASSET_FOLDER, 'tile_dirt.png'))
    border_image = pygame.image.load(os.path.join(ASSET_FOLDER, 'tile_cave.png'))
    lava_tile = pygame.image.load(os.path.join(ASSET_FOLDER, 'tile_lava.png'))
    water_tile = pygame.image.load(os.path.join(ASSET_FOLDER, 'tile_water.png'))
    stone_tile = pygame.image.load(os.path.join(ASSET_FOLDER, 'tile_stone.png'))
    wood_tile = pygame.image.load(os.path.join(ASSET_FOLDER, 'tile_wood.png'))

#now scale the images to the correct size for the game.
    background_image = pygame.transform.scale(background_image, TILE_SIZE) # this will scale
    border_image = pygame.transform.scale(border_image, TILE_SIZE) # this will scale the border image to the correct size for the game.
    lava_tile = pygame.transform.scale(lava_tile, TILE_SIZE) # Scale the lava tile image to the correct size for the game.
    water_tile = pygame.transform.scale(water_tile, TILE_SIZE) # Scale the water tile image to the correct size for the game.i
    stone_tile = pygame.transform.scale(stone_tile, TILE_SIZE) # Scale the stone tile image to the correct size for the game.
    wood_tile = pygame.transform.scale(wood_tile, TILE_SIZE) # Scale the wood tile image to the correct size for the game.

    # Barrier/wall tiles are solid fills: do NOT colorkey black, otherwise the
    # dark mortar becomes transparent and shows through as a black grid.
    return {
        'background_image': background_image,
        'border_image': border_image,
        'lava_tile': lava_tile,
        'water_tile': water_tile,
        'stone_tile': stone_tile,
        'wood_tile': wood_tile
        }

def load_object_images():
    gem_emeral = pygame.image.load(_first_existing(['gem_emeral.png', 'gem_emerald.png', 'gem_green.png']))
    gem_ruby = pygame.image.load(_first_existing(['gem_ruby.png', 'gem_red.png']))
    gem_sapphire = pygame.image.load(_first_existing(['gem_sapphire.png', 'gem_blue.png', 'gem_green.png']))
    door_closed = pygame.image.load(os.path.join(ASSET_FOLDER, 'doorClosed.png'))
    door_open = pygame.image.load(os.path.join(ASSET_FOLDER, 'doorOpen.png'))

    gem_emeral = pygame.transform.scale(gem_emeral, TILE_SIZE) # Scale the blue gem image to the correct size for the game.
    gem_ruby = pygame.transform.scale(gem_ruby, TILE_SIZE) # Scale the red gem image to the correct size for the game.
    gem_sapphire = pygame.transform.scale(gem_sapphire, TILE_SIZE) # Scale the blue gem image to the correct size for the game.
    door_closed = pygame.transform.scale(door_closed, TILE_SIZE)
    door_open = pygame.transform.scale(door_open, TILE_SIZE)
    
    door_closed.set_colorkey((0,0,0))
    door_open.set_colorkey((0,0,0))
    gem_emeral.set_colorkey((0,0,0))
    gem_ruby.set_colorkey((0,0,0))
    gem_sapphire.set_colorkey((0,0,0))


    
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

