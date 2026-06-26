#tu es la canard 

'''
a dungon puzzle explorere, where you the duck enter hell and battle deamons. 
a map and level build framework implimented in python & and clickly clickly excel. 
'''


## dir structure and plan 

home/ 
|---maps/
|   |--- map1.csv       #containers raw level configuration WORLD STATE
|
|---rules/ 
|   |--- objects.csv   # containes and describes objects in maps. OBJECT DEFINIATION
|   |--- movement.py   # describes movement of player and enemies. 
|   |--- colsion_ruels.py # rules for interaction between objects and players. 
|   |--- level_loader.py   # cordinates level choice and maps loaded. 
|
|---Source/ 
|   |--- map1.ods      # map editor source file.
| 
|---Assets/ 
|   |---sprits/        #png images 
|   |--- audio/        #sound affects music
|
|---Scripts
|   |--- main_menu.py       # menu screen/ death screen/ level picker. 
|   |--- score_timer.py     # clock timer, some kind of higher score per level. 
|   |--- scores.csv         # saves highscore data
|   |--- main.py            # Master script.  
|
|---launcher.py             # Main urnnng script
|---README.MD               # repo instructions/ plan / this doc 




