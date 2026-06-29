try:
    from .sprits import load_duck_images, load_enemy_images, load_enviromental_images
except ImportError:
    from sprits import load_duck_images, load_enemy_images, load_enviromental_images
import pygame

from rules.interactions import _barrier_rect

DUCK_SPEED = 5
barriers = []

# Populated from rules/objects.csv ability_rule, e.g. "blocks:border|wood".
enemy_collision_rules = {
    'enemy_fire': {'border'},
    'enemy_water': {'border'},
    'enemy_rock': {'border'},
}


def configure_enemy_collision_rules(object_defs):
    global enemy_collision_rules

    updated = dict(enemy_collision_rules)
    for obj in object_defs.values():
        if obj.get('object_type') != 'enemy':
            continue

        object_name = obj.get('object_name')
        rule = (obj.get('ability_rule') or '').strip()
        if not object_name:
            continue

        if rule.startswith('blocks:'):
            raw = rule.split(':', 1)[1]
            blocked = {name.strip() for name in raw.split('|') if name.strip()}
            updated[object_name] = blocked

    enemy_collision_rules = updated


def _barrier_name(barrier):
    if isinstance(barrier, tuple) and len(barrier) >= 3:
        return barrier[2]
    return None


def _enemy_should_block(enemy_name, barrier):
    barrier_name = _barrier_name(barrier)
    if not barrier_name:
        return False

    blocked = enemy_collision_rules.get(enemy_name)
    if blocked is None:
        return False

    return barrier_name in blocked


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
                rect = _barrier_rect(barrier)
                if rect and self.rect.colliderect(rect):
                    self.rect.top = rect.bottom
        elif direction == 'down':
            self.rect.y += self.speed
            self.image = self.images['front']
            for barrier in barriers:
                rect = _barrier_rect(barrier)
                if rect and self.rect.colliderect(rect):
                    self.rect.bottom = rect.top
        elif direction == 'right':
            self.rect.x += self.speed
            self.image = self.images['right']
            for barrier in barriers:
                rect = _barrier_rect(barrier)
                if rect and self.rect.colliderect(rect):
                    self.rect.right = rect.left
        elif direction == 'left':
            self.rect.x -= self.speed
            self.image = self.images['left']
            for barrier in barriers:
                rect = _barrier_rect(barrier)
                if rect and self.rect.colliderect(rect):
                    self.rect.left = rect.right

#define class enemy 
class Enemy_fire:
    def __init__(self, x, y):
        self.images = load_enemy_images()# Load the enemy image using the load_enemy_images function.
        self.image = self.images['enemy_fire']
        self.rect = self.image.get_rect(center =(x, y))
        self.speed = 3
        self.type = 'fire'
        self.object_name = 'enemy_fire'
        self.direction = 1  # 1 for right, -1 for left
    
    def move(self):
        self.rect.x += self.speed  * self.direction # Move the enemy to the right
        if self.rect.left > 800:  # If the enemy goes off the screen, reset its position self.direction = -1  # Change direction to left if self.rect.right < 0:  # If the enemy goes off the screen, reset its position
            self.direction = -1  # Change direction to right
        if self.rect.right < 0:
            self.direction = 1  # Change direction to left
        for barrier in barriers:
            if not _enemy_should_block(self.object_name, barrier):
                continue
            rect = _barrier_rect(barrier)
            if self.rect.colliderect(rect):
                if self.direction == 1:  # Moving right
                    self.rect.right = rect.left
                else:  # Moving left
                    self.rect.left = rect.right
                self.direction *= -1  # Reverse direction


class Enemy_water:
    def __init__(self, x, y):
        self.images = load_enemy_images()# Load the enemy image using the load_enemy_images function.
        self.image = self.images['enemy_water']
        self.rect = self.image.get_rect(center =(x, y))
        self.speed = 2
        self.type = 'water'
        self.object_name = 'enemy_water'
        self.direction = 1  # 1 for right, -1 for left
    
    def move(self):
        self.rect.x += self.speed  * self.direction # Move the enemy to the right
        if self.rect.left > 800:  # If the enemy goes off the screen, reset its position self.direction = -1  # Change direction to left if self.rect.right < 0:  # If the enemy goes off the screen, reset its position
            self.direction = -1  # Change direction to right
        if self.rect.right < 0:
            self.direction = 1 #change to right 

        for barrier in barriers:
            if not _enemy_should_block(self.object_name, barrier):
                continue
            rect = _barrier_rect(barrier)
            if rect and self.rect.colliderect(rect):
                if self.direction == 1:  # Moving right
                    self.rect.right = rect.left
                else:  # Moving left
                    self.rect.left = rect.right
                self.direction *= -1

class Enemy_rock:
    def __init__(self, x, y):
        self.images = load_enemy_images()# Load the enemy image using the load_enemy_images function.
        self.image = self.images['enemy_rock']
        self.rect = self.image.get_rect(center =(x, y))
        self.speed = 2
        self.type = 'rock' 
        self.object_name = 'enemy_rock'
        self.direction = 1  # 1 for right, -1 for left
    
    def move(self):
        self.rect.y += self.speed  * self.direction # Move the enemy to the right
        if self.rect.top > 600:  # If the enemy goes off the screen, reset its position self.direction = -1  # Change direction to left if self.rect.right < 0:  # If the enemy goes off the screen, reset its position
            self.direction = -1  # Change direction to right
        if self.rect.bottom < 0:
            self.direction = 1

        for barrier in barriers:
            if not _enemy_should_block(self.object_name, barrier):
                continue

            rect = _barrier_rect(barrier)
            if self.rect.colliderect(rect):
                if self.direction == 1:  # Moving down
                    self.rect.bottom = rect.top
                else:  # Moving up
                    self.rect.top = rect.bottom
                self.direction *= -1  # Reverse direction
