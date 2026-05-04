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
   - has a move(direction) method '''

import pygame
# Constants
ASSET_FOLDER = 'assets'
DUCK_SPEED = 5
DUCK_SIZE = (50, 50)
ENEMY_SIZE = (50, 50)

def load_duck_images():
    duck_front= pygame.image.load(f'{ASSET_FOLDER}\duck_front.png')
    duck_back = pygame.image.load(f'{ASSET_FOLDER}\duck_back.png')
    duck_right = pygame.image.load(f'{ASSET_FOLDER}\duck_walk_1.png')
    duck_left = pygame.image.load(f'{ASSET_FOLDER}\duck_walk_2.png')# this need to be inverted
    duck_left = pygame.transform.flip(duck_left, True, False)  # Flip the image horizontally

    #scale the images so they can be defined with DUCK_SIZE
    duck_front = pygame.transform.scale(duck_front, DUCK_SIZE)
    duck_back = pygame.transform.scale(duck_back, DUCK_SIZE)
    duck_right = pygame.transform.scale(duck_right, DUCK_SIZE)
    duck_left = pygame.transform.scale(duck_left, DUCK_SIZE)

    return {
        'front': duck_front,
        'back': duck_back,
        'right': duck_right,
        'left': duck_left
    }

def load_enemy_images():
    enemy_fire = pygame.image.load(f'{ASSET_FOLDER}\enemy_fire.png')
    enemy_water = pygame.image.load(f'{ASSET_FOLDER}\enemy_water.png')
    enemy_rock = pygame.image.load(f'{ASSET_FOLDER}\enemy_rock.png')
    #scale the images so they can be defined with ENEMY_SIZE
    enemy_fire = pygame.transform.scale(enemy_fire, ENEMY_SIZE)
    enemy_water = pygame.transform.scale(enemy_water, ENEMY_SIZE)
    enemy_rock = pygame.transform.scale(enemy_rock, ENEMY_SIZE)
    
    return {
        'enemy_fire': enemy_fire,
        'enemy_water': enemy_water,
        'enemy_rock': enemy_rock
    }

class duck:
    def __init__(self, x, y):
        self.images = load_duck_images()
        self.image = self.images['front']
        self.rect = self.image.get_rect(center=(x, y)) # this ancords the image. 
        self.speed = DUCK_SPEED

#define user input for duck movement
    def handle_input(self, keys):
        if keys[pygame.K_UP]:
            self.move('up')
        elif keys[pygame.K_DOWN]:
            self.move('down')
        elif keys[pygame.K_RIGHT]:
            self.move('right')
        elif keys[pygame.K_LEFT]:
            self.move('left')

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


#define class enemy  just use a square as a place holder. 
class Enemy:
    def __init__(self, x, y):
        self.images = load_enemy_images()# Load the enemy image using the load_enemy_images function.
        self.image = self.images['enemy_fire']
        self.rect = self.image.get_rect(center =(x, y))
        self.speed = 3
        self.type = 'fire'
        self.direction = 1  # 1 for right, -1 for left
    
    def move(self):
        self.rect.x += self.speed  * self.direction # Move the enemy to the right
        if self.rect.left > 800:  # If the enemy goes off the screen, reset its position self.direction = -1  # Change direction to left if self.rect.right < 0:  # If the enemy goes off the screen, reset its position
            self.direction = -1  # Change direction to right
        if self.rect.right < 0:
            self.direction = 1  # Change direction to left
