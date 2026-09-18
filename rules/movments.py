import pygame

try:
    from .sprits import load_duck_images, load_enemy_images
except ImportError:
    from sprits import load_duck_images, load_enemy_images

from rules.interactions import _barrier_rect


DUCK_SPEED = 300
barriers = []
PLAYER_HITBOX_SCALE = 0.8

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
        if object_name and rule.startswith('blocks:'):
            raw = rule.split(':', 1)[1]
            updated[object_name] = {
                name.strip() for name in raw.split('|') if name.strip()
            }
    enemy_collision_rules = updated


def _barrier_name(barrier):
    if isinstance(barrier, tuple) and len(barrier) >= 3:
        return barrier[2]
    return None


def _enemy_should_block(enemy_name, barrier):
    barrier_name = _barrier_name(barrier)
    return barrier_name in enemy_collision_rules.get(enemy_name, set())


class duck:
    def __init__(self, x, y):
        self.images = load_duck_images()
        self.image = self.images['front']
        self.rect = self.image.get_rect(center=(x, y))
        self.rect.inflate_ip(
            -round(self.rect.width * (1 - PLAYER_HITBOX_SCALE)),
            -round(self.rect.height * (1 - PLAYER_HITBOX_SCALE)),
        )
        self.position = pygame.Vector2(self.rect.center)
        self.speed = DUCK_SPEED

    def handle_input(self, keys, delta_seconds):
        if keys[pygame.K_UP]:
            self.move('up', delta_seconds)
        elif keys[pygame.K_DOWN]:
            self.move('down', delta_seconds)
        elif keys[pygame.K_RIGHT]:
            self.move('right', delta_seconds)
        elif keys[pygame.K_LEFT]:
            self.move('left', delta_seconds)

    def move(self, direction, delta_seconds):
        distance = self.speed * delta_seconds
        if direction == 'up':
            self.position.y -= distance
            self.rect.centery = round(self.position.y)
            self.image = self.images['back']
            if self._resolve_vertical(-1):
                self.position.y = self.rect.centery
        elif direction == 'down':
            self.position.y += distance
            self.rect.centery = round(self.position.y)
            self.image = self.images['front']
            if self._resolve_vertical(1):
                self.position.y = self.rect.centery
        elif direction == 'right':
            self.position.x += distance
            self.rect.centerx = round(self.position.x)
            self.image = self.images['right']
            if self._resolve_horizontal(1):
                self.position.x = self.rect.centerx
        elif direction == 'left':
            self.position.x -= distance
            self.rect.centerx = round(self.position.x)
            self.image = self.images['left']
            if self._resolve_horizontal(-1):
                self.position.x = self.rect.centerx

    def _resolve_horizontal(self, direction):
        collided = False
        for barrier in barriers:
            rect = _barrier_rect(barrier)
            if rect and self.rect.colliderect(rect):
                collided = True
                if direction > 0:
                    self.rect.right = rect.left
                else:
                    self.rect.left = rect.right
        return collided

    def _resolve_vertical(self, direction):
        collided = False
        for barrier in barriers:
            rect = _barrier_rect(barrier)
            if rect and self.rect.colliderect(rect):
                collided = True
                if direction > 0:
                    self.rect.bottom = rect.top
                else:
                    self.rect.top = rect.bottom
        return collided


class _HorizontalEnemy:
    speed = 0
    image_key = ''
    object_name = ''
    enemy_type = ''

    def __init__(self, x, y):
        self.images = load_enemy_images()
        self.image = self.images[self.image_key]
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.Vector2(self.rect.center)
        self.type = self.enemy_type
        self.direction = 1

    def move(self, delta_seconds):
        self.position.x += self.speed * self.direction * delta_seconds
        self.rect.centerx = round(self.position.x)
        collided = False
        for barrier in barriers:
            if not _enemy_should_block(self.object_name, barrier):
                continue
            rect = _barrier_rect(barrier)
            if rect and self.rect.colliderect(rect):
                collided = True
                if self.direction > 0:
                    self.rect.right = rect.left
                else:
                    self.rect.left = rect.right
                self.direction *= -1
        if collided:
            self.position.x = self.rect.centerx


class Enemy_fire(_HorizontalEnemy):
    speed = 180
    image_key = 'enemy_fire'
    object_name = 'enemy_fire'
    enemy_type = 'fire'


class Enemy_water(_HorizontalEnemy):
    speed = 120
    image_key = 'enemy_water'
    object_name = 'enemy_water'
    enemy_type = 'water'


class Enemy_rock:
    def __init__(self, x, y):
        self.images = load_enemy_images()
        self.frames = self.images['enemy_rock']
        self.frame_index = 0
        self.frame_elapsed = 0.0
        self.image = self.frames['up'][0]
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.Vector2(self.rect.center)
        self.speed = 60
        self.type = 'rock'
        self.object_name = 'enemy_rock'
        self.direction = 1
        self.animation_seconds_per_frame = 8 / 60

    def move(self, delta_seconds):
        self.position.y += self.speed * self.direction * delta_seconds
        self.rect.centery = round(self.position.y)
        collided = False
        for barrier in barriers:
            if not _enemy_should_block(self.object_name, barrier):
                continue
            rect = _barrier_rect(barrier)
            if rect and self.rect.colliderect(rect):
                collided = True
                if self.direction > 0:
                    self.rect.bottom = rect.top
                else:
                    self.rect.top = rect.bottom
                self.direction *= -1
        if collided:
            self.position.y = self.rect.centery

        frame_key = 'up' if self.direction > 0 else 'down'
        frames = self.frames[frame_key]
        self.frame_elapsed += delta_seconds
        if self.frame_elapsed >= self.animation_seconds_per_frame:
            self.frame_elapsed %= self.animation_seconds_per_frame
            self.frame_index = (self.frame_index + 1) % len(frames)
        self.image = frames[self.frame_index % len(frames)]
