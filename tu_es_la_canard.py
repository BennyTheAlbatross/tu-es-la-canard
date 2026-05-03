# you are the duck.
# Tu es le canard.
'''remembering a game from you youth, you were a duck (or you hade to kill the duck, not sure), hunt for gems, 2d game. 
''' 
# author: benny 

import pygame
import sys
import os

from Duck_movments import load_duck_images, Duck 

# define current dir to link to assests and utilities. use same dir as the script for now.
current_dir = os.path.dirname(os.path.abspath(__file__))

def main():
   # Initialise the screen 
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tu es le canard")
    
    # fill the background dark blue, add a boarder or dark purple. 
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 50)) # dark blue background
    boarder_color = (50, 0, 50) # dark purple color for the border
    pygame.draw.rect(background, boarder_color, background.get_rect(), 50) # draw the border with a thickness of 5 pixels


    # load the duck sprite, use the front image for now, we can add more later.
    duck_images = load_duck_images(f"{current_dir}/assets")
    duck_image, duck_rect = create_duck(duck_images, center=(400, 300))

    # main game loop
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # move the duck with arrow keys and change the sprite to the correct direction.
        keys = pygame.key.get_pressed()
        duck_image = move_duck(duck_rect, keys, duck_images, duck_image)
        
        # draw everything
        screen.blit(background, (0, 0))
        screen.blit(duck_image, duck_rect)
        pygame.display.flip()
        
        clock.tick(60)  # limit to 60 frames per second
if __name__ == "__main__":
    main()
