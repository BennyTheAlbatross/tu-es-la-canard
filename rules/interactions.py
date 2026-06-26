import pygame
import os 
try:
    from .movments import duck
except ImportError:
    from movments import duck


rules_dir = os.path.dirname(os.path.abspath(__file__))
objects_file = f'{rules_dir}\\objects.csv'




def barrier(player, barriers):
    player_rect = player.rect

    for b in barriers:
        if isinstance(b, pygame.Rect):
            rect = b
        else:
            # tuple format from your build_world: (x, y, name)
            x, y, _name = b
            rect = pygame.Rect(x, y, 50, 50)

        if player_rect.colliderect(rect):
            # Simple resolution: push player out based on overlap
            dx_left = abs(player_rect.right - rect.left)
            dx_right = abs(rect.right - player_rect.left)
            dy_top = abs(player_rect.bottom - rect.top)
            dy_bottom = abs(rect.bottom - player_rect.top)

            min_overlap = min(dx_left, dx_right, dy_top, dy_bottom)

            if min_overlap == dx_left:
                player_rect.right = rect.left
            elif min_overlap == dx_right:
                player_rect.left = rect.right
            elif min_overlap == dy_top:
                player_rect.bottom = rect.top
            else:
                player_rect.top = rect.bottom

    return player

def enemy(player, enemies):
    # Return alive flag + optional hit enemy
    # enemies can be objects with .rect OR tuples (x, y, name)
    for e in enemies:
        if hasattr(e, "rect"):
            enemy_rect = e.rect
        else:
            x, y, _name = e
            enemy_rect = pygame.Rect(x, y, 50, 50)

        if player.rect.colliderect(enemy_rect):
            return False, e

    return True, None

def gem(player, gems):
    # Return remaining gems + collected gem names
    remaining = []
    collected = []

    for g in gems:
        if hasattr(g, "rect"):
            gem_rect = g.rect
            gem_name = getattr(g, "name", "gem")
        else:
            x, y, gem_name = g
            gem_rect = pygame.Rect(x, y, 50, 50)

        if player.rect.colliderect(gem_rect):
            collected.append(gem_name)
        else:
            remaining.append(g)

    return remaining, collected




