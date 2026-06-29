import pygame 
import csv 
import os
import sys 

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

from rules.sprits import (
    TILE_SIZE,
    load_duck_images,
    load_enemy_images,
    load_enviromental_images as enviromental_images,
    load_object_images as object_images,
)
from rules.movments import duck, Enemy_fire, Enemy_water, Enemy_rock
import rules.movments as movments 
from rules import interactions


#constants 
HOME_DIR = os.path.dirname(CURRENT_DIR)
map_file = os.path.join(HOME_DIR, 'maps', 'game', 'map2.csv')
rules_file = os.path.join(HOME_DIR, 'rules', 'objects.csv')
#but this must be able tto be over written my the menu, but fiene for now.
screen_width = 800
screen_height = 400

# Visual underlay for enemy spawn tiles so enemy cells are not empty.
ENEMY_BASE_TILES = {
    'enemy_fire': 'lava',
    'enemy_water': 'water',
    'enemy_rock': 'stone',
}

# Visual underlay for gem spawn tiles.
GEM_BASE_TILES = {
    'gem_emerald': 'lava',
    'gem_ruby': 'water',
    'gem_sapphire': 'stone',
}

# Player spawn should render over normal background (tile 0 look).
PLAYER_BASE_TILE = 'background'

BACKGROUND_TILES = {
    'background': 'background_image',
    'lava': 'lava_tile',
    'water': 'water_tile',
    'stone': 'stone_tile',
    'wood': 'wood_tile',
}

BARRIER_TILES = {
    'border': 'border_image',
    'lava': 'lava_tile',
    'water': 'water_tile',
    'stone': 'stone_tile',
    'wood': 'wood_tile',
}

#define loads object 
def load_objects():
    by_id = {}
    with open(rules_file, 'r') as f:
        for row in csv.DictReader(f):
            by_id[int(row['object_number'])] = row 

        return by_id

#define build worlds from the map
def build_world(object_defs):
    background = []
    barriers = []
    enemies = []
    gems = []
    doors = []
    player_spawns = []
    max_used_col = 0
    max_used_row = 0

    with open(map_file, 'r') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, cell in enumerate(row):
                try:
                    object_id = int(cell)
                except ValueError:
                    # Skip header values like Column1 and BOM-prefixed cells.
                    continue

                obj = object_defs.get(object_id)
                if not obj:
                    continue

                # Track bounds from real placed objects, not trailing CSV empties.
                max_used_col = max(max_used_col, c + 1)
                max_used_row = max(max_used_row, r + 1)

                x = c * TILE_SIZE[0]
                y = r * TILE_SIZE[1]
                object_type = obj['object_type']
                object_name = obj['object_name']

                if object_type == 'background':
                    background.append((x, y, object_name))
                elif object_type == 'barrier':
                    barriers.append((x, y, object_name))
                elif object_type == 'enemy':
                    base_tile = ENEMY_BASE_TILES.get(object_name)
                    if base_tile:
                        # Keep enemy underlay visual-only; do not add to barriers.
                        background.append((x, y, base_tile))

                    center_x = x + TILE_SIZE[0] // 2
                    center_y = y + TILE_SIZE[1] // 2
                    if object_name == 'enemy_fire':
                        enemies.append(Enemy_fire(center_x, center_y))
                    elif object_name == 'enemy_water':
                        enemies.append(Enemy_water(center_x, center_y))
                    elif object_name == 'enemy_rock':
                        enemies.append(Enemy_rock(center_x, center_y))
                elif object_type == 'gem':
                    gem_base_tile = GEM_BASE_TILES.get(object_name)
                    if gem_base_tile:
                        # Keep gem underlay visual-only; do not add to barriers.
                        background.append((x, y, gem_base_tile))
                    gems.append((x, y, object_name))
                elif object_type == 'door':
                    # Keep door over normal background and track as a separate object.
                    background.append((x, y, 'background'))
                    doors.append((x, y, object_name))
                elif object_type == 'player':
                    # Keep player underlay visual-only; do not add to barriers.
                    background.append((x, y, PLAYER_BASE_TILE))
                    player_spawns.append((x, y))

    world_width = max_used_col * TILE_SIZE[0]
    world_height = max_used_row * TILE_SIZE[1]
    movments.barriers = barriers
    return background, barriers, enemies, gems, doors, player_spawns, world_width, world_height


def build_static_world_surface(world_width, world_height, background, barriers, env_images):
    # Pre-render static tile layers once and only draw dynamic objects every frame.
    static_world = pygame.Surface((world_width, world_height)).convert()
    static_world.fill((0, 0, 0))

    for x, y, name in background:
        image_key = BACKGROUND_TILES.get(name, 'background_image')
        static_world.blit(env_images[image_key], (x, y))

    for x, y, name in barriers:
        image_key = BARRIER_TILES.get(name, 'lava_tile')
        static_world.blit(env_images[image_key], (x, y))

    return static_world
    

    
def draw_world(screen, static_world, enemies, gems, doors, door_open, player, obj_images, camera_x=0, camera_y=0):

    tile_w, tile_h = TILE_SIZE
    view_left = camera_x - tile_w
    view_top = camera_y - tile_h
    view_right = camera_x + screen_width + tile_w
    view_bottom = camera_y + screen_height + tile_h

    # Draw the camera window from the pre-rendered static world.
    view_rect = pygame.Rect(camera_x, camera_y, screen_width, screen_height)
    screen.fill((0, 0, 0))
    screen.blit(static_world, (0, 0), area=view_rect)

    for enemy in enemies:
        if enemy.rect.right < view_left or enemy.rect.left > view_right or enemy.rect.bottom < view_top or enemy.rect.top > view_bottom:
            continue
        screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y - camera_y))

    for x, y, name in gems:
        if x < view_left or x > view_right or y < view_top or y > view_bottom:
            continue
        if name == 'gem_emerald':
            key = 'gem_emeral'
        else:
            key = name
        image = obj_images.get(key)
        if image is None:
            continue
        screen.blit(image, (x - camera_x, y - camera_y))

    for x, y, _name in doors:
        if x < view_left or x > view_right or y < view_top or y > view_bottom:
            continue
        key = 'door_open' if door_open else 'door_closed'
        image = obj_images.get(key)
        if image is None:
            continue
        screen.blit(image, (x - camera_x, y - camera_y))

    screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))


def main():
    pygame.init()

    duck_images = load_duck_images()
    enemy_images = load_enemy_images()
    env_images = enviromental_images()
    obj_images = object_images()

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tu es le canard")

    object_defs = load_objects()
    movments.configure_enemy_collision_rules(object_defs)
    background, barriers, enemies, gems, doors, player_spawns, world_width, world_height = build_world(object_defs)
    static_world = build_static_world_surface(world_width, world_height, background, barriers, env_images)

    if player_spawns:
        spawn_x, spawn_y = player_spawns[-1]
        player = duck(spawn_x + TILE_SIZE[0] // 2, spawn_y + TILE_SIZE[1] // 2)
    else:
        player = duck(screen_width // 2, screen_height // 2)

    camera_x = 0 
    camera_y = 0 
    clock = pygame.time.Clock()

    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Handle user input
        keys = pygame.key.get_pressed()
        player.handle_input(keys)

        # Move enemies
        for enemy in enemies:
            enemy.move()

        # Run interactions
        # First apply barrier collisions with current door state.
        door_is_open = len(gems) == 0
        active_barriers = barriers if door_is_open else barriers + doors
        player = interactions.barrier(player, active_barriers)
        alive, _hit_enemy = interactions.enemy(player, enemies)
        if not alive:
            print("GAME OVER")
            pygame.quit()
            sys.exit()
        gems, _collected = interactions.gem(player, gems)

        # Recompute after collecting gems this frame so door opens immediately.
        door_is_open = len(gems) == 0
        level_complete = interactions.door(player, doors, door_is_open)
        if level_complete:
            print("LEVEL COMPLETE")
            pygame.quit()
            sys.exit()

        # Update camera position to follow the player
        camera_x = player.rect.centerx - screen_width // 2
        camera_y = player.rect.centery - screen_height // 2

        # Clamp camera to map bounds for consistent framing across maps.
        max_camera_x = max(0, world_width - screen_width)
        max_camera_y = max(0, world_height - screen_height)
        camera_x = max(0, min(camera_x, max_camera_x))
        camera_y = max(0, min(camera_y, max_camera_y))

        draw_world(screen, static_world, enemies, gems, doors, door_is_open, player, obj_images, camera_x, camera_y)


        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)



if __name__ == "__main__":  
    main()






