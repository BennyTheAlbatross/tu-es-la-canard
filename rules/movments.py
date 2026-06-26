try:
    from .sprits import load_duck_images, load_enemy_images, load_enviromental_images
except ImportError:
    from sprits import load_duck_images, load_enemy_images, load_enviromental_images
import pygame 

DUCK_SPEED = 5
barriers = []


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
            for barrier in barriers:
                if self.rect.colliderect(barrier):
                    self.rect.top = barrier.bottom
        elif direction == 'down':
            self.rect.y += self.speed
            self.image = self.images['front']
            for barrier in barriers:
                if self.rect.colliderect(barrier):
                    self.rect.bottom = barrier.top
        elif direction == 'right':
            self.rect.x += self.speed
            self.image = self.images['right']
            for barrier in barriers:
                if self.rect.colliderect(barrier):
                    self.rect.right =barrier.left
        elif direction == 'left':
            self.rect.x -= self.speed
            self.image = self.images['left']
            for barrier in barriers:
                if self.rect.colliderect(barrier):
                    self.rect.left =barrier.right

#define class enemy 
class Enemy_fire:
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


class Enemy_water:
    def __init__(self, x, y):
        self.images = load_enemy_images()# Load the enemy image using the load_enemy_images function.
        self.image = self.images['enemy_water']
        self.rect = self.image.get_rect(center =(x, y))
        self.speed = 2
        self.type = 'water'
        self.direction = 1  # 1 for right, -1 for left
    
    def move(self):
        self.rect.x += self.speed  * self.direction # Move the enemy to the right
        if self.rect.left > 800:  # If the enemy goes off the screen, reset its position self.direction = -1  # Change direction to left if self.rect.right < 0:  # If the enemy goes off the screen, reset its position
            self.direction = -1  # Change direction to right
        if self.rect.right < 0:
            self.direction = 1 #change to right 

class Enemy_rock:
    def __init__(self, x, y):
        self.images = load_enemy_images()# Load the enemy image using the load_enemy_images function.
        self.image = self.images['enemy_rock']
        self.rect = self.image.get_rect(center =(x, y))
        self.speed = 2
        self.type = 'rock' 
        self.direction = 1  # 1 for right, -1 for left
    
    def move(self):
        self.rect.y += self.speed  * self.direction # Move the enemy to the right
        if self.rect.top > 600:  # If the enemy goes off the screen, reset its position self.direction = -1  # Change direction to left if self.rect.right < 0:  # If the enemy goes off the screen, reset its position
            self.direction = -1  # Change direction to right
        if self.rect.bottom < 0:
            self.direction = 1