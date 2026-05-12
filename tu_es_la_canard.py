# you are the duck.
# Tu es le canard.
'''remembering a game from you youth, you were a duck (or you hade to kill the duck, not sure), hunt for gems, 2d game. 
''' 
# author: benny 

import pygame
import sys
import os
import Duck_movments
from Duck_movments import duck, Enemy_fire, Enemy_water 
import map

# define current dir to link to assests and utilities. use same dir as the script for now.
current_dir = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = 'assets'

def main():
    # srart py game
    pygame.init()
   # Initialise the screen 
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tu es le canard")
    
#import textuers here and scale them to the correct size for the game.
    background_image = pygame.image.load(os.path.join(current_dir, 'assets', 'tile_dirt.png')).convert()
    border_image = pygame.image.load(os.path.join(current_dir, 'assets', 'tile_cave.png')).convert()
#now scale the images to the correct size for the game.
    background_image = pygame.transform.scale(background_image, (50, 50)) # this will scale
    border_image = pygame.transform.scale(border_image, (50, 50)) # this will scale the border image to the correct size for the game.

    background = pygame.Surface(screen.get_size())
    background = background.convert()

    #draw the image across the entire background, tile it to fill the screen.
    tile_width = background_image.get_width()
    tile_height = background_image.get_height()

    for x in range(0,800, tile_width):
        for y in range(0,600, tile_height):
            background.blit(background_image, (x, y)) # draw the background image across the entire screen.

    border_thickness = 40
    cave_width = border_image.get_width()
    cave_height = border_image.get_height()

    for x in range(0, 800, cave_width):
        for y in range(0, border_thickness, cave_height):
            background.blit(border_image, (x, y)) # draw the top border
            background.blit(border_image, (x, 600 - border_thickness + y)) # draw the bottom border

    for y in range(0, 600, cave_height):
        for x in range(0, border_thickness, cave_width):
            background.blit(border_image, (x, y)) # draw the left border
            background.blit(border_image, (800 - border_thickness + x, y)) # draw the right border
            
    lava_tile = pygame.image.load(f"{ASSETS_DIR}/tile_lava.png") # Load the lava tile image using pygame's image loading function.
    lava_tile = pygame.transform.scale(lava_tile, (50, 50)) # Scale the lava tile image to the correct size for the game.
    barriers = []
    Duck_movments.barriers = barriers # this will allow us to use the barriers list in the duck class for collision detection.
    #add the borders to the barrier list, so the duck can collide with them.
    barriers.append(pygame.Rect(0, 0, 800, border_thickness)) # top border
    barriers.append(pygame.Rect(0, 600 - border_thickness, 800, border_thickness)) # bottom border
    barriers.append(pygame.Rect(0, 0, border_thickness, 600)) # left border
    barriers.append(pygame.Rect(800 - border_thickness, 0, border_thickness, 600)) # right border
    lava = map.create_obstacles() # this will create the lava obstacles using the create_obstacles function from the map module.
    barriers.extend(map.create_obstacles())

    for block in lava:
        for x in range(block.left, block.right, 50):
            for y in range(block.top, block.bottom, 50):
                screen.blit(lava_tile, (x, y))

    


    # start clock
    clock = pygame.time.Clock()
    # create one duck at the center of the screen.
    player_duck = duck( 400, 300)
    #create the an enemy list
    enemy1 = Enemy_fire(100, 100) # thes will create an enemy at the top left corner of the screen.
    enemy2 = Enemy_water(700, 500) # this will create an enemy at the bottom right corner of the screen.

    enemy_list = [enemy1,enemy2]
 
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # move the duck with arrow keys and change the sprite to the correct direction.
        keys = pygame.key.get_pressed()
        player_duck.handle_input(keys) # this function should be defined in the duck class
        #call enemys in list and activate them. 
        for enemy in enemy_list:
            enemy.move() 
        
        # draw everything
        screen.blit(background, (0, 0)) 
        screen.blit(player_duck.image, player_duck.rect) # this assumes the duck class has an image and rect attribute for drawing
        for enemy in enemy_list:
            screen.blit(enemy.image, enemy.rect)
        pygame.display.flip()
        clock.tick(60)  # limit to 60 frames per second
        #collision logic, when the duck collises with the enemy from enemy list , the game should print "game over" and stop loop. 
        for enemy in enemy_list:
            if player_duck.rect.colliderect(enemy.rect): # this will check if the duck collides with any enemy in the enemy list.
                print(" GAME OVER ")
                exit()

if __name__ == "__main__": # this is the standard way to run the main function in Python, it checks if the script is being run directly (as the main program) and not imported as a module in another script. If this condition is true, it calls the main() function to start the game. 
    main()
