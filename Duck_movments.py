''' duck_movement.py

1. constants
   - asset folder
   - duck speed
   - duck size

2. image-loading function
   - loads front/back/right/left images
   - returns them in a useful structure

3. Duck class
   - stores image, rect, spee
   - has a move(direction) method
'''

import pygame
# Constants
ASSET_FOLDER = 'assets'
DUCK_SPEED = 5
DUCK_SIZE = (50, 50)

def load_duck_images():
    duck_frunt = pygame.image.load(f'{ASSET_FOLDER}/duck_front.png')
    duck_back = pygame.image.load(f'{ASSET_FOLDER}/duck_back.png')
    duck_right = pygame.image.load(f'{ASSET_FOLDER}/duck_walk1.png')
    duck_left = pygame.image.load(f'{ASSET_FOLDER}/duck_walk2.png')# this need to be inverted
    duck_left = pygame.transform.flip(duck_left, True, False)  # Flip the image horizontally
    return {
        'front': duck_frunt,
        'back': duck_back,
        'right': duck_right,
        'left': duck_left
    }

class Duck:
    def __init__(self, x, y)
        self.images = load_duck_images()
        self.image = self.images['front']
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = DUCK_SPEED

    def move(self, direction):
        if direction == 'up':
            self.rect.y -= self.speed
            self.image = self.images['back']
        elif direction == 'down':
            self.rect.y += self.speed
            self.image = self.images['front']
        elif direction == 'right':
            self.rect.x += self.speed
            self.image = self.images['right']
        elif direction == 'left':
            self.rect.x -= self.speed
            self.image = self.images['left']
