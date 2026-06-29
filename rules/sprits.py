
import os
import pygame
# Constants
RULES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(RULES_DIR)
ASSET_FOLDER = os.path.join(PROJECT_DIR, 'assets')
DUCK_SPEED = 5
TILE_SIZE = (30, 30)


def _first_existing(candidates):
    for filename in candidates:
        path = os.path.join(ASSET_FOLDER, filename)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f'None of these files were found: {candidates}')

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

    return {
        'front': duck_front,
        'back': duck_back,
        'right': duck_right,
        'left': duck_left
    }

def load_enemy_images():
    enemy_fire = pygame.image.load(os.path.join(ASSET_FOLDER, 'enemy_fire.png'))
    enemy_water = pygame.image.load(os.path.join(ASSET_FOLDER, 'enemy_water.png'))
    enemy_rock = pygame.image.load(os.path.join(ASSET_FOLDER, 'enemy_rock.png'))
    #scale the images so they can be defined with ENEMY_SIZE
    enemy_fire = pygame.transform.scale(enemy_fire, TILE_SIZE)
    enemy_water = pygame.transform.scale(enemy_water, TILE_SIZE)
    enemy_rock = pygame.transform.scale(enemy_rock, TILE_SIZE)
    
    return {
        'enemy_fire': enemy_fire,
        'enemy_water': enemy_water,
        'enemy_rock': enemy_rock
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
    door_closed = pygame.image.load(_first_existing(['door_closed.png', 'door_part_01.png']))
    door_open = pygame.image.load(_first_existing(['door_open.png', 'door_part_02.png', 'door_part_01.png']))

    gem_emeral = pygame.transform.scale(gem_emeral, TILE_SIZE) # Scale the blue gem image to the correct size for the game.
    gem_ruby = pygame.transform.scale(gem_ruby, TILE_SIZE) # Scale the red gem image to the correct size for the game.
    gem_sapphire = pygame.transform.scale(gem_sapphire, TILE_SIZE) # Scale the blue gem image to the correct size for the game.
    door_closed = pygame.transform.scale(door_closed, TILE_SIZE)
    door_open = pygame.transform.scale(door_open, TILE_SIZE)

    return {
        'gem_emeral': gem_emeral,
        'gem_ruby': gem_ruby,
        'gem_sapphire': gem_sapphire,
        'door_closed': door_closed,
        'door_open': door_open,
        } 
