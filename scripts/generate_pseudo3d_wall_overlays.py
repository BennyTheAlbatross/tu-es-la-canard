#!/usr/bin/env python3
"""Generate crisp, tile-sized pseudo-3D wall overlays without Pillow."""

from pathlib import Path
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "tiles" / "walls_pseudo3d"
SIZE = 40


def blank():
    return pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)


def save(name, surface):
    pygame.image.save(surface, OUTPUT / name)


def main():
    pygame.init()
    OUTPUT.mkdir(parents=True, exist_ok=True)

    north = blank()
    pygame.draw.rect(north, (198, 190, 166, 150), (1, 0, 38, 1))
    pygame.draw.line(north, (145, 137, 117, 110), (4, 2), (15, 2))
    pygame.draw.line(north, (145, 137, 117, 90), (24, 2), (35, 2))
    save("north_highlight.png", north)

    west = blank()
    pygame.draw.rect(west, (178, 170, 147, 125), (0, 1, 1, 38))
    pygame.draw.line(west, (136, 130, 110, 85), (2, 5), (2, 16))
    pygame.draw.line(west, (136, 130, 110, 70), (2, 24), (2, 34))
    save("west_highlight.png", west)

    east = blank()
    pygame.draw.rect(east, (19, 20, 19, 105), (37, 1, 3, 38))
    pygame.draw.line(east, (45, 44, 39, 120), (36, 6), (36, 18))
    pygame.draw.line(east, (45, 44, 39, 120), (36, 25), (36, 34))
    save("east_shade.png", east)

    south = blank()
    pygame.draw.rect(south, (18, 18, 17, 188), (0, 33, 40, 7))
    pygame.draw.line(south, (121, 112, 93, 160), (1, 32), (38, 32))
    pygame.draw.line(south, (64, 60, 52, 210), (0, 36), (39, 36))
    pygame.draw.line(south, (90, 82, 68, 145), (11, 33), (11, 36))
    pygame.draw.line(south, (8, 9, 8, 190), (27, 37), (27, 39))
    pygame.draw.line(south, (42, 41, 36, 180), (28, 37), (35, 37))
    save("south_face.png", south)

    shadow_south = blank()
    pygame.draw.rect(shadow_south, (4, 5, 5, 92), (0, 0, 40, 2))
    pygame.draw.rect(shadow_south, (4, 5, 5, 52), (1, 2, 38, 2))
    pygame.draw.line(shadow_south, (4, 5, 5, 24), (3, 4), (36, 4))
    save("contact_shadow_south.png", shadow_south)

    shadow_east = blank()
    pygame.draw.rect(shadow_east, (4, 5, 5, 72), (0, 0, 2, 40))
    pygame.draw.rect(shadow_east, (4, 5, 5, 38), (2, 1, 2, 38))
    save("contact_shadow_east.png", shadow_east)

    pygame.quit()


if __name__ == "__main__":
    main()
