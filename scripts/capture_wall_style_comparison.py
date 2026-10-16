#!/usr/bin/env python3
"""Capture classic and pseudo-3D renders at the same Tutorial camera position."""

from pathlib import Path
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules import shaders
from rules.hazards import CollapsingFloor
from rules.movments import duck
from rules.sprits import (
    TILE_SIZE,
    load_collapsing_floor_images,
    load_enviromental_images,
    load_mechanic_images,
    load_object_images,
    load_torch_images,
)
from rules.wall_rendering import WALL_STYLE_CLASSIC, WALL_STYLE_PSEUDO3D, load_pseudo3d_overlays
from runtime.gameplay import (
    build_static_world_surface,
    build_world,
    draw_world,
    load_objects,
    screen_height,
    screen_width,
)


def main():
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    env_images = load_enviromental_images()
    object_images = load_object_images()
    torch_frames = load_torch_images()
    floor_images = load_collapsing_floor_images()
    mechanic_images = load_mechanic_images()
    overlays = load_pseudo3d_overlays()

    (
        background,
        barriers,
        enemies,
        gems,
        doors,
        torches,
        floor_positions,
        gates,
        hidden_doors,
        player_spawns,
        world_width,
        world_height,
        tile_map,
    ) = build_world(load_objects(), ROOT / "maps" / "game" / "map5.csv")

    spawn_x, spawn_y = player_spawns[-1]
    player = duck(spawn_x + TILE_SIZE[0] // 2, spawn_y + TILE_SIZE[1] // 2)
    player.set_torch(True)
    camera_x = max(0, min(player.rect.centerx - screen_width // 2, world_width - screen_width))
    camera_y = max(0, min(player.rect.centery - screen_height // 2, world_height - screen_height))
    effects = shaders.EnvironmentEffects(tile_map=tile_map, tile_size=TILE_SIZE[0])
    floors = [CollapsingFloor(x, y, floor_images) for x, y in floor_positions]

    output = ROOT / "docs" / "screenshots"
    output.mkdir(parents=True, exist_ok=True)
    for style, filename in (
        (WALL_STYLE_CLASSIC, "2d-walls-classic.png"),
        (WALL_STYLE_PSEUDO3D, "2d-walls-pseudo3d.png"),
    ):
        static_world, animated_tiles = build_static_world_surface(
            world_width,
            world_height,
            background,
            barriers,
            gates,
            env_images,
            mechanic_images,
            wall_style=style,
            wall_overlays=overlays,
        )
        draw_world(
            screen,
            static_world,
            animated_tiles,
            enemies,
            gems,
            doors,
            False,
            torches,
            floors,
            hidden_doors,
            mechanic_images,
            torch_frames,
            0,
            player,
            object_images,
            camera_x,
            camera_y,
            effects=effects,
            time_seconds=0.0,
        )
        pygame.image.save(screen, output / filename)
    pygame.quit()


if __name__ == "__main__":
    main()
