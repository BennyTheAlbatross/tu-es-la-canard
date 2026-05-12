import pygame

ASSETS_DIR = 'assets'

def create_obstacles():
    lava_tile = pygame.image.load(f"{ASSETS_DIR}/tile_lava.png") # Load the lava tile image using pygame's image loading function.
    lava_tile = pygame.transform.scale(lava_tile, (50, 50)) # Scale the lava tile image to the correct size for the game.
    lava = []
    lava.append(pygame.Rect(200, 150, 100, 50))
    lava.append(pygame.Rect(400, 300, 50, 200))
    lava.append(pygame.Rect(600, 100, 150, 50))
    return lava 
