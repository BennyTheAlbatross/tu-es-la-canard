"""Neighbour-aware pseudo-3D wall composition for the top-down renderer."""

import os

import pygame

from rules.sprits import ASSET_FOLDER, TILE_SIZE


WALL_STYLE_CLASSIC = "classic"
WALL_STYLE_PSEUDO3D = "pseudo3d"
WALL_STYLES = (WALL_STYLE_CLASSIC, WALL_STYLE_PSEUDO3D)

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

PSEUDO3D_WALL_NAMES = frozenset(("border", "stone"))
OVERLAY_DIR = os.path.join(ASSET_FOLDER, "tiles", "walls_pseudo3d")
OVERLAY_FILES = {
    "north_highlight": "north_highlight.png",
    "west_highlight": "west_highlight.png",
    "east_shade": "east_shade.png",
    "south_face": "south_face.png",
    "shadow_east": "contact_shadow_east.png",
    "shadow_south": "contact_shadow_south.png",
}


def normalise_wall_style(value):
    """Return a supported style, defaulting unknown values to pseudo3d."""
    if value and str(value).strip().lower() == WALL_STYLE_CLASSIC:
        return WALL_STYLE_CLASSIC
    return WALL_STYLE_PSEUDO3D


def wall_cells(barriers):
    """Return grid coordinates for walls that form one connected stone mass."""
    tile_w, tile_h = TILE_SIZE
    return {
        (y // tile_h, x // tile_w)
        for x, y, name in barriers
        if name in PSEUDO3D_WALL_NAMES
    }


def neighbour_mask(cells, row, column):
    """Encode cardinal wall neighbours as NORTH/EAST/SOUTH/WEST bits."""
    mask = 0
    if (row - 1, column) in cells:
        mask |= NORTH
    if (row, column + 1) in cells:
        mask |= EAST
    if (row + 1, column) in cells:
        mask |= SOUTH
    if (row, column - 1) in cells:
        mask |= WEST
    return mask


def load_pseudo3d_overlays():
    """Load pixel-art overlays once; never mutate the original wall assets."""
    overlays = {}
    for name, filename in OVERLAY_FILES.items():
        image = pygame.image.load(os.path.join(OVERLAY_DIR, filename)).convert_alpha()
        if image.get_size() != TILE_SIZE:
            image = pygame.transform.scale(image, TILE_SIZE)
        overlays[name] = image
    return overlays


def build_wall_variant_cache(env_images, overlays, barriers):
    """Compose only the wall/mask combinations present in the loaded map."""
    cells = wall_cells(barriers)
    variants = {}
    for x, y, name in barriers:
        if name not in PSEUDO3D_WALL_NAMES:
            continue
        row = y // TILE_SIZE[1]
        column = x // TILE_SIZE[0]
        mask = neighbour_mask(cells, row, column)
        image_key = "border_image" if name == "border" else "stone_tile"
        cache_key = (image_key, mask)
        if cache_key in variants:
            continue

        variant = env_images[image_key].copy()
        if not mask & NORTH:
            variant.blit(overlays["north_highlight"], (0, 0))
        if not mask & WEST:
            variant.blit(overlays["west_highlight"], (0, 0))
        if not mask & EAST:
            variant.blit(overlays["east_shade"], (0, 0))
        if not mask & SOUTH:
            variant.blit(overlays["south_face"], (0, 0))
        variants[cache_key] = variant
    return cells, variants


def iter_contact_shadows(cells, world_columns, world_rows):
    """Yield floor-cell shadows beside exposed south and east wall edges."""
    for row, column in cells:
        if row + 1 < world_rows and (row + 1, column) not in cells:
            yield column * TILE_SIZE[0], (row + 1) * TILE_SIZE[1], "shadow_south"
        if column + 1 < world_columns and (row, column + 1) not in cells:
            yield (column + 1) * TILE_SIZE[0], row * TILE_SIZE[1], "shadow_east"
