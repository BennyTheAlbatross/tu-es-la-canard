import pygame 
import csv 
import os
import sys 

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

from rules.sprits import (
    load_duck_images,
    load_enemy_images,
    load_enviromental_images as enviromental_images,
    load_object_images as object_images,
)
from rules.movments import duck, Enemy_fire, Enemy_water, Enemy_rock
from rules import interactions


#constants 
HOME_DIR = F'{CURRENT_DIR}\\..'
map_file = f'{HOME_DIR}\\maps\\game\\map1.csv'
rules_file = f'{HOME_DIR}\\rules\\objects.csv'
#but this must be able tto be over written my the menu, but fiene for now.
screen_width = 800
screen_height = 600

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
    player_spawns = []

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

                x = c * 50
                y = r * 50
                object_type = obj['object_type']
                object_name = obj['object_name']

                if object_type == 'background':
                    background.append((x, y, object_name))
                elif object_type == 'barrier':
                    barriers.append((x, y, object_name))
                elif object_type == 'enemy':
                    center_x = x + 25
                    center_y = y + 25
                    if object_name == 'enemy_fire':
                        enemies.append(Enemy_fire(center_x, center_y))
                    elif object_name == 'enemy_water':
                        enemies.append(Enemy_water(center_x, center_y))
                    elif object_name == 'enemy_rock':
                        enemies.append(Enemy_rock(center_x, center_y))
                elif object_type == 'gem':
                    gems.append((x, y, object_name))
                elif object_type == 'player':
                    player_spawns.append((x, y))

    return background, barriers, enemies, gems, player_spawns
    
def draw_world(screen, background, barriers, enemies, gems, player, enemy_images, env_images, obj_images):
    for x, y, _name in background:
        screen.blit(env_images['background_image'], (x, y))

    for x, y, name in barriers:
        image = env_images['border_image'] if name == 'border' else env_images['lava_tile']
        screen.blit(image, (x, y))

    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect)

    for x, y, name in gems:
        if name == 'gem_emerald':
            key = 'gem_emeral'
        else:
            key = name
        image = obj_images.get(key)
        if image is None:
            continue
        screen.blit(image, (x, y))

    screen.blit(player.image, player.rect)


def main():
    pygame.init()

    duck_images = load_duck_images()
    enemy_images = load_enemy_images()
    env_images = enviromental_images()
    obj_images = object_images()

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tu es le canard")

    object_defs = load_objects()
    background, barriers, enemies, gems, player_spawns = build_world(object_defs)

    if player_spawns:
        spawn_x, spawn_y = player_spawns[0]
        player = duck(spawn_x + 25, spawn_y + 25)
    else:
        player = duck(screen_width // 2, screen_height // 2)

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
        player = interactions.barrier(player, barriers)
        alive, _hit_enemy = interactions.enemy(player, enemies)
        if not alive:
            print("GAME OVER")
            pygame.quit()
            sys.exit()
        gems, _collected = interactions.gem(player, gems)

        draw_world(screen, background, barriers, enemies, gems, player, enemy_images, env_images, obj_images)

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        pygame.time.Clock().tick(60)


if __name__ == "__main__":  
    main()






