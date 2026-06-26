import pygame
import sys
import os

state = "menu"

if state == "menu": 
    draw menu 
    ENTER -> state = game "game" 

if state == "game"
    run game logic here. 
if state == "loss": 
    draw loss screen. 
    R -- reset-> 
    M --> menu. 

draw_menu()
draw_loss_screen()
reset_game()


def menu():
    screen = pygame.display.set_mode((800, 600))
