import pygame  # pygame obvs 
import os      # to find files?? 
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
MAPS_DIR = f"{current_dir}/maps/game"
ASSETS_DIR = 'assets'
map1 = f"{MAPS_DIR}/map1.csv"
print(map1)

lava_DF = pd.read_csv(map1)
lava_list = []
def create_obstacles():
    lava_tile = pygame.image.load(f"{ASSETS_DIR}/tile_lava.png") # Load the lava tile image using pygame's image loading function.
    lava_tile = pygame.transform.scale(lava_tile, (50, 50)) # Scale the lava tile image to the correct size for the game.
    for row_number, row_data in lava_DF.iterrows():   # go through each row: 
        for col_number, lava in enumerate(row_data):  # then each col in the rows 
            if lava == 1:
                x = col_number * 50
                y = row_number * 50 
                lava_list.append(pygame.Rect( x, y, 50, 50))
                print(f"added lava at {x} {y}" )
    return lava_list 


create_obstacles()

