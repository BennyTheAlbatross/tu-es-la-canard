"""
shaders.py

Environmental rendering and lighting effects for Tu es la Canard.

This module provides:

1. Automatic wall-edge shadows.
2. Continuous animated lava and water overlays.
3. Random floor details placed outside the tile grid.
4. Player, torch, gem, lava, and water glow.
5. A darkness overlay with soft illuminated areas.

The tile map remains responsible for:
- level layout;
- collision;
- object placement;
- gameplay rules.

This module merely adds visual polish above the normal map rendering.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterable, Sequence

import csv
import os

import pygame

try:
    from .sprits import TILE_SIZE as SPRITE_TILE_SIZE
except ImportError:
    from sprits import TILE_SIZE as SPRITE_TILE_SIZE


# =============================================================================
# OBJECT NUMBERS
# =============================================================================
#
# These are loaded directly from objects.csv so that nothing is hard coded.
#
# Each constant is looked up by its object_name and set to the matching
# object_number. If the CSV layout changes, these values follow automatically.
# =============================================================================

_RULES_DIR = os.path.dirname(os.path.abspath(__file__))
_OBJECTS_CSV = os.path.join(_RULES_DIR, "objects.csv")


def _load_object_numbers(csv_path: str = _OBJECTS_CSV) -> dict[str, int]:
    """Read objects.csv and map each object_name to its object_number."""

    numbers: dict[str, int] = {}

    with open(csv_path, "r", newline="") as handle:
        for row in csv.DictReader(handle):
            name = (row.get("object_name") or "").strip()
            raw_number = (row.get("object_number") or "").strip()

            if not name or not raw_number:
                continue

            try:
                numbers[name] = int(raw_number)
            except ValueError:
                continue

    return numbers


OBJECT_NUMBERS = _load_object_numbers()

BACKGROUND = OBJECT_NUMBERS["background"]
BORDER = OBJECT_NUMBERS["border"]
LAVA = OBJECT_NUMBERS["lava"]

ENEMY_FIRE = OBJECT_NUMBERS["enemy_fire"]
ENEMY_WATER = OBJECT_NUMBERS["enemy_water"]
ENEMY_ROCK = OBJECT_NUMBERS["enemy_rock"]

GEM_EMERALD = OBJECT_NUMBERS["gem_emerald"]
GEM_RUBY = OBJECT_NUMBERS["gem_ruby"]
GEM_SAPPHIRE = OBJECT_NUMBERS["gem_sapphire"]

DUCK = OBJECT_NUMBERS["duck"]
WATER = OBJECT_NUMBERS["water"]
STONE = OBJECT_NUMBERS["stone"]
WOOD = OBJECT_NUMBERS["wood"]
END_DOOR = OBJECT_NUMBERS["end_door"]
TORCH = OBJECT_NUMBERS["torch"]


# =============================================================================
# GENERAL SETTINGS
# =============================================================================

# Match the project's sprite tile size source-of-truth.
# The sprite module stores this as a (width, height) tuple.
if isinstance(SPRITE_TILE_SIZE, (tuple, list)) and SPRITE_TILE_SIZE:
    TILE_SIZE = int(SPRITE_TILE_SIZE[0])
else:
    TILE_SIZE = int(SPRITE_TILE_SIZE)

# Changing this seed changes where randomly generated bones and stones appear.
# Keeping it fixed means details appear in the same places every time.
DECORATION_RANDOM_SEED = 7319


# =============================================================================
# DARKNESS SETTINGS
# =============================================================================
#
# 0   = no darkness
# 255 = completely black
#
# Something between 170 and 220 usually works well.
# =============================================================================

DARKNESS_ENABLED = True
DARKNESS_ALPHA = 201

# Number of circles used to make each light soft.
# Higher values are smoother, but cost more performance.
LIGHT_GRADIENT_LAYERS = 10


# =============================================================================
# WALL SHADOW SETTINGS
# =============================================================================
#
# Shadows are generated automatically wherever a solid tile touches a
# non-solid tile.
#
# WALL_SHADOW_OUTSIDE controls how far the shadow falls onto the floor.
# WALL_SHADE_INSIDE controls how far darkness extends inside the wall.
# =============================================================================

WALL_SHADOW_ENABLED = True

WALL_SHADOW_COLOUR = (0, 0, 0)
WALL_SHADOW_ALPHA = 22

# Shadow cast outward from the wall, as a fraction of TILE_SIZE.
WALL_SHADOW_OUTSIDE = 0.05

# Darkened strip inside the edge of the wall.
WALL_SHADE_INSIDE = 0.02

# Extra darkness used at corners.
CORNER_SHADOW_ALPHA = 10


# =============================================================================
# LAVA ANIMATION SETTINGS
# =============================================================================
#
# The lava overlay is generated across each whole connected pool.
# It does not restart independently inside every tile.
# =============================================================================

LAVA_ANIMATION_ENABLED = True

LAVA_BASE_COLOUR = (210, 42, 8)
LAVA_BRIGHT_COLOUR = (255, 190, 30)
LAVA_DARK_COLOUR = (110, 12, 4)

LAVA_OVERLAY_ALPHA = 28

# Pixel movement per second.
LAVA_SCROLL_SPEED_X = 0.0
LAVA_SCROLL_SPEED_Y = 0.0

# Controls the spacing and movement of glowing lines.
LAVA_WAVE_SPACING = 34
LAVA_WAVE_THICKNESS = 3
LAVA_WAVE_SPEED = 0.0

# General light produced by lava.
LAVA_GLOW_ENABLED = False
LAVA_GLOW_COLOUR = (255, 75, 15)
LAVA_GLOW_RADIUS = 65
LAVA_GLOW_STRENGTH = 22


# =============================================================================
# WATER ANIMATION SETTINGS
# =============================================================================

WATER_ANIMATION_ENABLED = True

WATER_BASE_COLOUR = (15, 60, 125)
WATER_BRIGHT_COLOUR = (55, 170, 230)
WATER_DARK_COLOUR = (5, 25, 80)

WATER_OVERLAY_ALPHA = 24

WATER_SCROLL_SPEED_X = 0.0
WATER_SCROLL_SPEED_Y = 0.0

WATER_WAVE_SPACING = 42
WATER_WAVE_THICKNESS = 2
WATER_WAVE_SPEED = 0.0

# Water can glow slightly, although far less than lava.
WATER_GLOW_ENABLED = False
WATER_GLOW_COLOUR = (30, 100, 190)
WATER_GLOW_RADIUS = 50
WATER_GLOW_STRENGTH = 14


# =============================================================================
# PLAYER LIGHT SETTINGS
# =============================================================================

# The player is the only active light. It uses a clear, clean colour that
# fades out smoothly across a few tiles.
PLAYER_GLOW_ENABLED = True
PLAYER_GLOW_COLOUR = (255, 244, 214)
PLAYER_GLOW_RADIUS = 250
PLAYER_GLOW_STRENGTH = 300

# No animation: the light stays perfectly still.
PLAYER_GLOW_PULSE_AMOUNT = 0
PLAYER_GLOW_PULSE_SPEED = 0.0


# =============================================================================
# TORCH LIGHT SETTINGS
# =============================================================================

TORCH_GLOW_ENABLED = True
TORCH_GLOW_COLOUR = (255, 105, 22)
TORCH_GLOW_RADIUS = 85
TORCH_GLOW_STRENGTH = 75

TORCH_FLICKER_AMOUNT = 1
TORCH_FLICKER_SPEED = 0.1


# =============================================================================
# GEM LIGHT SETTINGS
# =============================================================================

GEM_GLOW_ENABLED = False
EMERALD_GLOW_COLOUR = (35, 255, 105)
RUBY_GLOW_COLOUR = (255, 45, 45)
SAPPHIRE_GLOW_COLOUR = (35, 125, 255)

GEM_GLOW_RADIUS = 62
GEM_GLOW_STRENGTH = 60

GEM_PULSE_AMOUNT = 0
GEM_PULSE_SPEED = 0.0


# =============================================================================
# FLOOR DECORATION SETTINGS
# =============================================================================
#
# Floor decoration positions are chosen in world pixels, rather than once per
# tile. This helps hide the underlying grid.
# =============================================================================

FLOOR_DECORATIONS_ENABLED = False

# Approximate number of decorations per 100 floor tiles.
FLOOR_DECORATIONS_PER_100_TILES = 8

# Empty space kept around walls.
FLOOR_DECORATION_WALL_MARGIN = 8

# Empty space kept between decorations.
FLOOR_DECORATION_MINIMUM_DISTANCE = 30

# Allowed random rotations.
FLOOR_DECORATION_ROTATIONS = (0, 90, 180, 270)

# Decorations are placed only on these tile types.
FLOOR_TILE_TYPES = {BACKGROUND}

# Tiles that should cast wall shadows.
SOLID_TILE_TYPES = {
    BORDER,
    LAVA,
    WATER,
    STONE,
    WOOD,
}

# Fluid types.
FLUID_TILE_TYPES = {
    LAVA,
    WATER,
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class LightSource:
    """One light source in world coordinates."""

    x: float
    y: float
    radius: float
    colour: tuple[int, int, int]
    strength: int
    flicker_seed: float = 0.0


@dataclass
class FloorDecoration:
    """A decorative sprite placed in world coordinates."""

    image: pygame.Surface
    x: float
    y: float


@dataclass
class FluidRegion:
    """
    A connected collection of lava or water cells.

    The region has a local mask, which allows one continuous animated texture
    to be clipped to the exact connected shape.
    """

    tile_type: int
    cells: list[tuple[int, int]]

    world_x: int
    world_y: int

    width: int
    height: int

    mask: pygame.Surface


# =============================================================================
# SMALL UTILITY FUNCTIONS
# =============================================================================

def clamp(value: float, minimum: float, maximum: float) -> float:
    """Restrict a number to the supplied range."""

    return max(minimum, min(maximum, value))


def get_map_size(tile_map: Sequence[Sequence[int]]) -> tuple[int, int]:
    """Return map width and height in tiles."""

    if not tile_map:
        return 0, 0

    return len(tile_map[0]), len(tile_map)


def tile_at(
    tile_map: Sequence[Sequence[int]],
    row: int,
    column: int,
    outside_value: int = BORDER,
) -> int:
    """
    Safely obtain a map value.

    Anything outside the map is treated as a border.
    """

    if row < 0 or row >= len(tile_map):
        return outside_value

    if column < 0 or column >= len(tile_map[row]):
        return outside_value

    return tile_map[row][column]


def world_to_tile(
    world_x: float,
    world_y: float,
    tile_size: int,
) -> tuple[int, int]:
    """Convert world pixel coordinates into row and column coordinates."""

    column = int(world_x // tile_size)
    row = int(world_y // tile_size)

    return row, column


def is_floor_position(
    tile_map: Sequence[Sequence[int]],
    world_x: float,
    world_y: float,
    tile_size: int,
) -> bool:
    """Return True when the supplied world position lies on floor."""

    row, column = world_to_tile(world_x, world_y, tile_size)

    return tile_at(tile_map, row, column) in FLOOR_TILE_TYPES


def rect_is_on_floor(
    tile_map: Sequence[Sequence[int]],
    rectangle: pygame.Rect,
    tile_size: int,
    margin: int = 0,
) -> bool:
    """
    Check whether a rectangle and its margin are entirely over floor.

    This prevents bones and skulls from overlapping nearby walls.
    """

    test_rect = rectangle.inflate(margin * 2, margin * 2)

    points = (
        test_rect.topleft,
        test_rect.topright,
        test_rect.bottomleft,
        test_rect.bottomright,
        test_rect.center,
        test_rect.midtop,
        test_rect.midbottom,
        test_rect.midleft,
        test_rect.midright,
    )

    return all(
        is_floor_position(tile_map, point_x, point_y, tile_size)
        for point_x, point_y in points
    )


def object_value(game_object, name: str, default=None):
    """
    Obtain a value from either an object instance or a dictionary.

    This means the effects system can accept objects such as:

        {"object_number": 14, "x": 200, "y": 300}

    or class instances such as:

        game_object.object_number
        game_object.x
        game_object.y
    """

    if isinstance(game_object, dict):
        return game_object.get(name, default)

    return getattr(game_object, name, default)


def get_object_centre(game_object) -> tuple[float, float]:
    """
    Find an object's centre.

    Supported forms include:

    - object.rect.center
    - dictionary containing "rect"
    - x, y, width and height
    - x and y alone
    """

    rectangle = object_value(game_object, "rect")

    if rectangle is not None:
        return float(rectangle.centerx), float(rectangle.centery)

    x = float(object_value(game_object, "x", 0))
    y = float(object_value(game_object, "y", 0))

    width = float(object_value(game_object, "width", 0))
    height = float(object_value(game_object, "height", 0))

    return x + width / 2, y + height / 2


# =============================================================================
# FLUID REGION GENERATION
# =============================================================================

def find_connected_regions(
    tile_map: Sequence[Sequence[int]],
    target_tile_type: int,
) -> list[list[tuple[int, int]]]:
    """
    Find all connected regions containing the target tile type.

    Only north, south, east and west connections are counted.
    Diagonal contact does not merge two pools.
    """

    rows = len(tile_map)

    if rows == 0:
        return []

    columns = len(tile_map[0])

    visited: set[tuple[int, int]] = set()
    regions: list[list[tuple[int, int]]] = []

    for row in range(rows):
        for column in range(columns):
            if tile_map[row][column] != target_tile_type:
                continue

            if (row, column) in visited:
                continue

            region: list[tuple[int, int]] = []
            stack = [(row, column)]

            while stack:
                current_row, current_column = stack.pop()

                if (current_row, current_column) in visited:
                    continue

                if not (
                    0 <= current_row < rows
                    and 0 <= current_column < columns
                ):
                    continue

                if tile_map[current_row][current_column] != target_tile_type:
                    continue

                visited.add((current_row, current_column))
                region.append((current_row, current_column))

                stack.extend(
                    (
                        (current_row - 1, current_column),
                        (current_row + 1, current_column),
                        (current_row, current_column - 1),
                        (current_row, current_column + 1),
                    )
                )

            if region:
                regions.append(region)

    return regions


def build_fluid_region(
    cells: list[tuple[int, int]],
    tile_type: int,
    tile_size: int,
) -> FluidRegion:
    """Build a clipping mask for one connected fluid pool."""

    minimum_row = min(row for row, _ in cells)
    maximum_row = max(row for row, _ in cells)

    minimum_column = min(column for _, column in cells)
    maximum_column = max(column for _, column in cells)

    width = (maximum_column - minimum_column + 1) * tile_size
    height = (maximum_row - minimum_row + 1) * tile_size

    mask = pygame.Surface((width, height), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))

    for row, column in cells:
        local_x = (column - minimum_column) * tile_size
        local_y = (row - minimum_row) * tile_size

        pygame.draw.rect(
            mask,
            (255, 255, 255, 255),
            (local_x, local_y, tile_size, tile_size),
        )

    return FluidRegion(
        tile_type=tile_type,
        cells=cells,
        world_x=minimum_column * tile_size,
        world_y=minimum_row * tile_size,
        width=width,
        height=height,
        mask=mask,
    )


def generate_fluid_regions(
    tile_map: Sequence[Sequence[int]],
    tile_size: int,
) -> list[FluidRegion]:
    """Generate connected animation regions for all lava and water pools."""

    fluid_regions: list[FluidRegion] = []

    for tile_type in FLUID_TILE_TYPES:
        connected_regions = find_connected_regions(tile_map, tile_type)

        for cells in connected_regions:
            fluid_regions.append(
                build_fluid_region(
                    cells=cells,
                    tile_type=tile_type,
                    tile_size=tile_size,
                )
            )

    return fluid_regions


# =============================================================================
# CONTINUOUS FLUID ANIMATION
# =============================================================================

def create_fluid_animation_surface(
    region: FluidRegion,
    time_seconds: float,
) -> pygame.Surface:
    """
    Create an animated surface covering one whole fluid region.

    The animation is generated in region-wide pixel coordinates, so it does
    not visibly restart at tile boundaries.
    """

    surface = pygame.Surface(
        (region.width, region.height),
        pygame.SRCALPHA,
    )

    if region.tile_type == LAVA:
        base_colour = (*LAVA_BASE_COLOUR, LAVA_OVERLAY_ALPHA)
        bright_colour = (*LAVA_BRIGHT_COLOUR, LAVA_OVERLAY_ALPHA)
        dark_colour = (*LAVA_DARK_COLOUR, LAVA_OVERLAY_ALPHA)

        speed_x = LAVA_SCROLL_SPEED_X
        speed_y = LAVA_SCROLL_SPEED_Y

        spacing = LAVA_WAVE_SPACING
        thickness = LAVA_WAVE_THICKNESS
        wave_speed = LAVA_WAVE_SPEED

    else:
        base_colour = (*WATER_BASE_COLOUR, WATER_OVERLAY_ALPHA)
        bright_colour = (*WATER_BRIGHT_COLOUR, WATER_OVERLAY_ALPHA)
        dark_colour = (*WATER_DARK_COLOUR, WATER_OVERLAY_ALPHA)

        speed_x = WATER_SCROLL_SPEED_X
        speed_y = WATER_SCROLL_SPEED_Y

        spacing = WATER_WAVE_SPACING
        thickness = WATER_WAVE_THICKNESS
        wave_speed = WATER_WAVE_SPEED

    surface.fill(base_colour)

    x_offset = int(time_seconds * speed_x)
    y_offset = int(time_seconds * speed_y)

    # -------------------------------------------------------------------------
    # Dark moving bands
    # -------------------------------------------------------------------------

    for y in range(-spacing * 2, region.height + spacing * 2, spacing):
        moving_y = y + y_offset % spacing

        pygame.draw.line(
            surface,
            dark_colour,
            (-spacing, moving_y),
            (region.width + spacing, moving_y + spacing // 2),
            max(1, thickness + 1),
        )

    # -------------------------------------------------------------------------
    # Bright curved wave lines
    # -------------------------------------------------------------------------

    phase = time_seconds * wave_speed

    for base_y in range(-spacing, region.height + spacing, spacing):
        points: list[tuple[int, int]] = []

        for x in range(-10, region.width + 11, 10):
            world_phase_x = x + region.world_x + x_offset

            wave_y = (
                base_y
                + y_offset % spacing
                + math.sin(world_phase_x * 0.055 + phase) * 6
            )

            points.append((x, int(wave_y)))

        if len(points) >= 2:
            pygame.draw.lines(
                surface,
                bright_colour,
                False,
                points,
                thickness,
            )

    # -------------------------------------------------------------------------
    # Clip the animation to the connected pool shape
    # -------------------------------------------------------------------------

    surface.blit(
        region.mask,
        (0, 0),
        special_flags=pygame.BLEND_RGBA_MULT,
    )

    return surface


def draw_fluid_regions(
    screen: pygame.Surface,
    fluid_regions: Sequence[FluidRegion],
    camera_x: float,
    camera_y: float,
    time_seconds: float,
) -> None:
    """Draw all continuous lava and water animation overlays."""

    screen_rectangle = screen.get_rect()

    for region in fluid_regions:
        if region.tile_type == LAVA and not LAVA_ANIMATION_ENABLED:
            continue

        if region.tile_type == WATER and not WATER_ANIMATION_ENABLED:
            continue

        destination = pygame.Rect(
            int(region.world_x - camera_x),
            int(region.world_y - camera_y),
            region.width,
            region.height,
        )

        if not destination.colliderect(screen_rectangle):
            continue

        animation_surface = create_fluid_animation_surface(
            region,
            time_seconds,
        )

        screen.blit(animation_surface, destination.topleft)


# =============================================================================
# AUTOMATIC WALL SHADOWS
# =============================================================================

def draw_wall_shadows(
    screen: pygame.Surface,
    tile_map: Sequence[Sequence[int]],
    camera_x: float,
    camera_y: float,
    tile_size: int,
) -> None:
    """
    Draw automatic shadows where solid tiles meet non-solid tiles.

    The main shadow falls onto the open side of the boundary.

    A smaller shade is placed inside the solid tile to stop the transition
    looking like a perfectly straight pasted-on strip.
    """

    if not WALL_SHADOW_ENABLED:
        return

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    outside_width = max(1, int(tile_size * WALL_SHADOW_OUTSIDE))
    inside_width = max(1, int(tile_size * WALL_SHADE_INSIDE))

    rows = len(tile_map)

    if rows == 0:
        return

    columns = len(tile_map[0])

    for row in range(rows):
        for column in range(columns):
            tile_type = tile_map[row][column]

            if tile_type not in SOLID_TILE_TYPES:
                continue

            world_x = column * tile_size
            world_y = row * tile_size

            screen_x = int(world_x - camera_x)
            screen_y = int(world_y - camera_y)

            neighbours = {
                "top": tile_at(tile_map, row - 1, column),
                "bottom": tile_at(tile_map, row + 1, column),
                "left": tile_at(tile_map, row, column - 1),
                "right": tile_at(tile_map, row, column + 1),
            }

            # -----------------------------------------------------------------
            # Top boundary
            # -----------------------------------------------------------------

            if neighbours["top"] not in SOLID_TILE_TYPES:
                pygame.draw.rect(
                    overlay,
                    (*WALL_SHADOW_COLOUR, WALL_SHADOW_ALPHA),
                    (
                        screen_x,
                        screen_y - outside_width,
                        tile_size,
                        outside_width,
                    ),
                )

                pygame.draw.rect(
                    overlay,
                    (*WALL_SHADOW_COLOUR, WALL_SHADOW_ALPHA // 2),
                    (
                        screen_x,
                        screen_y,
                        tile_size,
                        inside_width,
                    ),
                )

            # -----------------------------------------------------------------
            # Bottom boundary
            # -----------------------------------------------------------------

            if neighbours["bottom"] not in SOLID_TILE_TYPES:
                pygame.draw.rect(
                    overlay,
                    (*WALL_SHADOW_COLOUR, WALL_SHADOW_ALPHA),
                    (
                        screen_x,
                        screen_y + tile_size,
                        tile_size,
                        outside_width,
                    ),
                )

                pygame.draw.rect(
                    overlay,
                    (*WALL_SHADOW_COLOUR, WALL_SHADOW_ALPHA // 2),
                    (
                        screen_x,
                        screen_y + tile_size - inside_width,
                        tile_size,
                        inside_width,
                    ),
                )

            # -----------------------------------------------------------------
            # Left boundary
            # -----------------------------------------------------------------

            if neighbours["left"] not in SOLID_TILE_TYPES:
                pygame.draw.rect(
                    overlay,
                    (*WALL_SHADOW_COLOUR, WALL_SHADOW_ALPHA),
                    (
                        screen_x - outside_width,
                        screen_y,
                        outside_width,
                        tile_size,
                    ),
                )

                pygame.draw.rect(
                    overlay,
                    (*WALL_SHADOW_COLOUR, WALL_SHADOW_ALPHA // 2),
                    (
                        screen_x,
                        screen_y,
                        inside_width,
                        tile_size,
                    ),
                )

            # -----------------------------------------------------------------
            # Right boundary
            # -----------------------------------------------------------------

            if neighbours["right"] not in SOLID_TILE_TYPES:
                pygame.draw.rect(
                    overlay,
                    (*WALL_SHADOW_COLOUR, WALL_SHADOW_ALPHA),
                    (
                        screen_x + tile_size,
                        screen_y,
                        outside_width,
                        tile_size,
                    ),
                )

                pygame.draw.rect(
                    overlay,
                    (*WALL_SHADOW_COLOUR, WALL_SHADOW_ALPHA // 2),
                    (
                        screen_x + tile_size - inside_width,
                        screen_y,
                        inside_width,
                        tile_size,
                    ),
                )

            # -----------------------------------------------------------------
            # Corner shadows
            # -----------------------------------------------------------------

            corner_size = outside_width

            if (
                neighbours["bottom"] not in SOLID_TILE_TYPES
                and neighbours["right"] not in SOLID_TILE_TYPES
            ):
                pygame.draw.rect(
                    overlay,
                    (*WALL_SHADOW_COLOUR, CORNER_SHADOW_ALPHA),
                    (
                        screen_x + tile_size,
                        screen_y + tile_size,
                        corner_size,
                        corner_size,
                    ),
                )

            if (
                neighbours["bottom"] not in SOLID_TILE_TYPES
                and neighbours["left"] not in SOLID_TILE_TYPES
            ):
                pygame.draw.rect(
                    overlay,
                    (*WALL_SHADOW_COLOUR, CORNER_SHADOW_ALPHA),
                    (
                        screen_x - corner_size,
                        screen_y + tile_size,
                        corner_size,
                        corner_size,
                    ),
                )

    screen.blit(overlay, (0, 0))


# =============================================================================
# RANDOM FLOOR DECORATIONS
# =============================================================================

def generate_floor_decorations(
    tile_map: Sequence[Sequence[int]],
    decoration_images: Sequence[pygame.Surface],
    tile_size: int,
    seed: int = DECORATION_RANDOM_SEED,
) -> list[FloorDecoration]:
    """
    Randomly distribute decorations across all open floor space.

    Placement happens in world pixels rather than at tile centres.

    Generate these once when the level loads. Do not call this every frame.
    """

    if not FLOOR_DECORATIONS_ENABLED:
        return []

    if not decoration_images:
        return []

    rows = len(tile_map)

    if rows == 0:
        return []

    columns = len(tile_map[0])

    floor_tile_count = sum(
        1
        for row in tile_map
        for tile_type in row
        if tile_type in FLOOR_TILE_TYPES
    )

    desired_count = round(
        floor_tile_count
        * FLOOR_DECORATIONS_PER_100_TILES
        / 100
    )

    world_width = columns * tile_size
    world_height = rows * tile_size

    generator = random.Random(seed)

    decorations: list[FloorDecoration] = []
    accepted_positions: list[pygame.Vector2] = []

    attempts = 0
    maximum_attempts = max(100, desired_count * 50)

    while (
        len(decorations) < desired_count
        and attempts < maximum_attempts
    ):
        attempts += 1

        original_image = generator.choice(decoration_images)
        angle = generator.choice(FLOOR_DECORATION_ROTATIONS)

        image = pygame.transform.rotate(original_image, angle)

        x = generator.randint(0, max(0, world_width - 1))
        y = generator.randint(0, max(0, world_height - 1))

        rectangle = image.get_rect(center=(x, y))

        if not rect_is_on_floor(
            tile_map,
            rectangle,
            tile_size,
            FLOOR_DECORATION_WALL_MARGIN,
        ):
            continue

        candidate_position = pygame.Vector2(x, y)

        too_close = any(
            candidate_position.distance_to(existing_position)
            < FLOOR_DECORATION_MINIMUM_DISTANCE
            for existing_position in accepted_positions
        )

        if too_close:
            continue

        decorations.append(
            FloorDecoration(
                image=image,
                x=x,
                y=y,
            )
        )

        accepted_positions.append(candidate_position)

    return decorations


def draw_floor_decorations(
    screen: pygame.Surface,
    decorations: Sequence[FloorDecoration],
    camera_x: float,
    camera_y: float,
) -> None:
    """Draw generated floor details with camera movement."""

    screen_rectangle = screen.get_rect()

    for decoration in decorations:
        destination = decoration.image.get_rect(
            center=(
                int(decoration.x - camera_x),
                int(decoration.y - camera_y),
            )
        )

        if destination.colliderect(screen_rectangle):
            screen.blit(decoration.image, destination)


# =============================================================================
# LIGHT SOURCE COLLECTION
# =============================================================================

def collect_object_lights(
    game_objects: Iterable,
    time_seconds: float,
) -> list[LightSource]:
    """
    Turn player, torch and gem objects into light sources.

    Every object must provide an object_number and a position.

    Accepted position forms:

        object.rect
        object.x and object.y
        dictionary entries with the same names
    """

    lights: list[LightSource] = []

    for game_object in game_objects:
        object_number = object_value(
            game_object,
            "object_number",
            object_value(game_object, "type_code"),
        )

        x, y = get_object_centre(game_object)

        # ---------------------------------------------------------------------
        # Player glow
        # ---------------------------------------------------------------------

        if object_number == DUCK:
            if not PLAYER_GLOW_ENABLED:
                continue

            pulse = math.sin(
                time_seconds * PLAYER_GLOW_PULSE_SPEED
            ) * PLAYER_GLOW_PULSE_AMOUNT

            lights.append(
                LightSource(
                    x=x,
                    y=y,
                    radius=PLAYER_GLOW_RADIUS + pulse,
                    colour=PLAYER_GLOW_COLOUR,
                    strength=PLAYER_GLOW_STRENGTH,
                )
            )

        # ---------------------------------------------------------------------
        # Torch glow
        # ---------------------------------------------------------------------

        elif object_number == TORCH:
            if not TORCH_GLOW_ENABLED:
                continue

            flicker_seed = x * 0.017 + y * 0.031

            flicker = (
                math.sin(
                    time_seconds * TORCH_FLICKER_SPEED
                    + flicker_seed
                )
                * TORCH_FLICKER_AMOUNT
            )

            lights.append(
                LightSource(
                    x=x,
                    y=y,
                    radius=TORCH_GLOW_RADIUS + flicker,
                    colour=TORCH_GLOW_COLOUR,
                    strength=TORCH_GLOW_STRENGTH,
                    flicker_seed=flicker_seed,
                )
            )

        # ---------------------------------------------------------------------
        # Emerald glow
        # ---------------------------------------------------------------------

        elif object_number == GEM_EMERALD:
            if not GEM_GLOW_ENABLED:
                continue

            pulse = math.sin(
                time_seconds * GEM_PULSE_SPEED + x * 0.01
            ) * GEM_PULSE_AMOUNT

            lights.append(
                LightSource(
                    x=x,
                    y=y,
                    radius=GEM_GLOW_RADIUS + pulse,
                    colour=EMERALD_GLOW_COLOUR,
                    strength=GEM_GLOW_STRENGTH,
                )
            )

        # ---------------------------------------------------------------------
        # Ruby glow
        # ---------------------------------------------------------------------

        elif object_number == GEM_RUBY:
            if not GEM_GLOW_ENABLED:
                continue

            pulse = math.sin(
                time_seconds * GEM_PULSE_SPEED + x * 0.01
            ) * GEM_PULSE_AMOUNT

            lights.append(
                LightSource(
                    x=x,
                    y=y,
                    radius=GEM_GLOW_RADIUS + pulse,
                    colour=RUBY_GLOW_COLOUR,
                    strength=GEM_GLOW_STRENGTH,
                )
            )

        # ---------------------------------------------------------------------
        # Sapphire glow
        # ---------------------------------------------------------------------

        elif object_number == GEM_SAPPHIRE:
            if not GEM_GLOW_ENABLED:
                continue

            pulse = math.sin(
                time_seconds * GEM_PULSE_SPEED + x * 0.01
            ) * GEM_PULSE_AMOUNT

            lights.append(
                LightSource(
                    x=x,
                    y=y,
                    radius=GEM_GLOW_RADIUS + pulse,
                    colour=SAPPHIRE_GLOW_COLOUR,
                    strength=GEM_GLOW_STRENGTH,
                )
            )

    return lights


def collect_fluid_lights(
    fluid_regions: Sequence[FluidRegion],
    tile_size: int,
) -> list[LightSource]:
    """
    Produce low-strength lights along lava and water regions.

    Lights are spaced apart, rather than adding one light for every tile.
    This avoids needless expense for large pools.
    """

    lights: list[LightSource] = []

    for region in fluid_regions:
        if region.tile_type == LAVA:
            if not LAVA_GLOW_ENABLED:
                continue

            glow_colour = LAVA_GLOW_COLOUR
            glow_radius = LAVA_GLOW_RADIUS
            glow_strength = LAVA_GLOW_STRENGTH

        else:
            if not WATER_GLOW_ENABLED:
                continue

            glow_colour = WATER_GLOW_COLOUR
            glow_radius = WATER_GLOW_RADIUS
            glow_strength = WATER_GLOW_STRENGTH

        # Use every second tile in large regions to keep performance sensible.
        for index, (row, column) in enumerate(region.cells):
            if len(region.cells) > 8 and index % 2 != 0:
                continue

            lights.append(
                LightSource(
                    x=column * tile_size + tile_size / 2,
                    y=row * tile_size + tile_size / 2,
                    radius=glow_radius,
                    colour=glow_colour,
                    strength=glow_strength,
                )
            )

    return lights


# =============================================================================
# SOFT LIGHT DRAWING
# =============================================================================

def draw_soft_light(
    light_surface: pygame.Surface,
    x: float,
    y: float,
    radius: float,
    colour: tuple[int, int, int],
    strength: int,
) -> None:
    """
    Draw one soft coloured radial light.

    This is used for additive coloured glow.
    """

    radius = max(1, int(radius))
    strength = int(clamp(strength, 0, 255))

    diameter = radius * 2

    local_surface = pygame.Surface(
        (diameter, diameter),
        pygame.SRCALPHA,
    )

    centre = (radius, radius)

    for layer in range(LIGHT_GRADIENT_LAYERS, 0, -1):
        progress = layer / LIGHT_GRADIENT_LAYERS

        layer_radius = int(radius * progress)

        # Squaring progress gives a softer outer fade.
        alpha = int(strength * (1.0 - progress) ** 2)

        pygame.draw.circle(
            local_surface,
            (*colour, alpha),
            centre,
            layer_radius,
        )

    # Clearer and brighter inner glow.
    pygame.draw.circle(
        local_surface,
        (*colour, min(255, strength)),
        centre,
        max(1, int(radius * 0.12)),
    )

    light_surface.blit(
        local_surface,
        (
            int(x - radius),
            int(y - radius),
        ),
        special_flags=pygame.BLEND_RGBA_ADD,
    )


def cut_soft_light_from_darkness(
    darkness_surface: pygame.Surface,
    x: float,
    y: float,
    radius: float,
    strength: int,
) -> None:
    """
    Remove darkness around a light source.

    This uses subtraction on the alpha channel of the darkness surface.
    """

    radius = max(1, int(radius))
    strength = int(clamp(strength, 0, 255))

    diameter = radius * 2

    cutout = pygame.Surface(
        (diameter, diameter),
        pygame.SRCALPHA,
    )

    centre = (radius, radius)

    for layer in range(LIGHT_GRADIENT_LAYERS, 0, -1):
        progress = layer / LIGHT_GRADIENT_LAYERS

        layer_radius = int(radius * progress)

        # Strongest removal at the centre.
        alpha_removal = int(
            strength * (1.0 - progress) ** 1.7
        )

        pygame.draw.circle(
            cutout,
            (0, 0, 0, alpha_removal),
            centre,
            layer_radius,
        )

    darkness_surface.blit(
        cutout,
        (
            int(x - radius),
            int(y - radius),
        ),
        special_flags=pygame.BLEND_RGBA_SUB,
    )


def draw_lighting(
    screen: pygame.Surface,
    light_sources: Sequence[LightSource],
    camera_x: float,
    camera_y: float,
) -> None:
    """
    Draw environmental darkness with lights cut out of it.

    A single darkness overlay is drawn over the scene, and each light simply
    subtracts from that darkness. No colour is added on top of the scene.
    """

    if not DARKNESS_ENABLED:
        return

    screen_size = screen.get_size()

    darkness_surface = pygame.Surface(
        screen_size,
        pygame.SRCALPHA,
    )

    darkness_surface.fill((0, 0, 0, DARKNESS_ALPHA))

    expanded_screen_rectangle = screen.get_rect().inflate(500, 500)

    for light in light_sources:
        screen_x = light.x - camera_x
        screen_y = light.y - camera_y

        light_rectangle = pygame.Rect(
            int(screen_x - light.radius),
            int(screen_y - light.radius),
            int(light.radius * 2),
            int(light.radius * 2),
        )

        if not light_rectangle.colliderect(expanded_screen_rectangle):
            continue

        cut_soft_light_from_darkness(
            darkness_surface=darkness_surface,
            x=screen_x,
            y=screen_y,
            radius=light.radius,
            strength=light.strength,
        )

    screen.blit(darkness_surface, (0, 0))


# =============================================================================
# MAIN EFFECTS MANAGER
# =============================================================================

class EnvironmentEffects:
    """
    Stores effects generated for one level.

    Create one instance when the level loads.

    Example:

        effects = EnvironmentEffects(
            tile_map=level_map,
            floor_decoration_images=[
                skull_image,
                bone_image,
                small_rock_image,
            ],
            tile_size=TILE_SIZE,
        )
    """

    def __init__(
        self,
        tile_map: Sequence[Sequence[int]],
        floor_decoration_images: Sequence[pygame.Surface] = (),
        tile_size: int = TILE_SIZE,
        decoration_seed: int = DECORATION_RANDOM_SEED,
    ) -> None:
        self.tile_map = tile_map
        self.tile_size = tile_size

        # Generated once because the map itself does not change every frame.
        self.fluid_regions = generate_fluid_regions(
            tile_map,
            tile_size,
        )

        self.floor_decorations = generate_floor_decorations(
            tile_map=tile_map,
            decoration_images=floor_decoration_images,
            tile_size=tile_size,
            seed=decoration_seed,
        )

    def rebuild(
        self,
        tile_map: Sequence[Sequence[int]] | None = None,
    ) -> None:
        """
        Rebuild region data after permanent map changes.

        Call this after altering lava, water, walls, or floor tiles.
        """

        if tile_map is not None:
            self.tile_map = tile_map

        self.fluid_regions = generate_fluid_regions(
            self.tile_map,
            self.tile_size,
        )

    def draw_floor_details(
        self,
        screen: pygame.Surface,
        camera_x: float,
        camera_y: float,
    ) -> None:
        """Draw bones, skulls, cracks, stones, and similar details."""

        draw_floor_decorations(
            screen=screen,
            decorations=self.floor_decorations,
            camera_x=camera_x,
            camera_y=camera_y,
        )

    def draw_fluids(
        self,
        screen: pygame.Surface,
        camera_x: float,
        camera_y: float,
        time_seconds: float,
    ) -> None:
        """Draw continuous lava and water animation overlays."""

        draw_fluid_regions(
            screen=screen,
            fluid_regions=self.fluid_regions,
            camera_x=camera_x,
            camera_y=camera_y,
            time_seconds=time_seconds,
        )

    def draw_shadows(
        self,
        screen: pygame.Surface,
        camera_x: float,
        camera_y: float,
    ) -> None:
        """Draw automatic wall and boundary shadows."""

        draw_wall_shadows(
            screen=screen,
            tile_map=self.tile_map,
            camera_x=camera_x,
            camera_y=camera_y,
            tile_size=self.tile_size,
        )

    def draw_lighting(
        self,
        screen: pygame.Surface,
        game_objects: Iterable,
        camera_x: float,
        camera_y: float,
        time_seconds: float,
    ) -> None:
        """Draw all fluid, player, torch and gem lighting."""

        object_lights = collect_object_lights(
            game_objects=game_objects,
            time_seconds=time_seconds,
        )

        fluid_lights = collect_fluid_lights(
            fluid_regions=self.fluid_regions,
            tile_size=self.tile_size,
        )

        all_lights = object_lights + fluid_lights

        draw_lighting(
            screen=screen,
            light_sources=all_lights,
            camera_x=camera_x,
            camera_y=camera_y,
        )