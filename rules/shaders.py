"""
shaders.py

Minimal lighting for Tu es la Canard.

This module provides only:

1. A darkness overlay.
2. The player light.
3. The torch light.

Lights are cut out of a single darkness surface; nothing is added on top of
the scene. The tile map remains responsible for layout, collision, object
placement and gameplay rules.
"""

from __future__ import annotations

import math
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
# Loaded directly from objects.csv so that nothing is hard coded.
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

GEM_EMERALD = OBJECT_NUMBERS["gem_emerald"]
GEM_RUBY = OBJECT_NUMBERS["gem_ruby"]
GEM_SAPPHIRE = OBJECT_NUMBERS["gem_sapphire"]

DUCK = OBJECT_NUMBERS["duck"]
TORCH = OBJECT_NUMBERS["torch"]


# =============================================================================
# TILE SIZE
# =============================================================================

if isinstance(SPRITE_TILE_SIZE, (tuple, list)) and SPRITE_TILE_SIZE:
    TILE_SIZE = int(SPRITE_TILE_SIZE[0])
else:
    TILE_SIZE = int(SPRITE_TILE_SIZE)


# =============================================================================
# DARKNESS SETTINGS
# =============================================================================
#
# 0   = no darkness
# 255 = completely black
# =============================================================================

DARKNESS_ENABLED = True
DARKNESS_ALPHA = 201

# Number of circles used to make each light soft.
LIGHT_GRADIENT_LAYERS = 10


# =============================================================================
# PLAYER LIGHT SETTINGS
# =============================================================================

PLAYER_GLOW_ENABLED = True
PLAYER_GLOW_COLOUR = (255, 244, 214)
PLAYER_GLOW_RADIUS = 100
PLAYER_GLOW_STRENGTH = 300

PLAYER_GLOW_PULSE_AMOUNT = 0
PLAYER_GLOW_PULSE_SPEED = 0.0


# =============================================================================
# TORCH LIGHT SETTINGS
# =============================================================================

TORCH_GLOW_ENABLED = True
TORCH_GLOW_COLOUR = (255, 205, 222)
TORCH_GLOW_RADIUS = 130
TORCH_GLOW_STRENGTH = 290

TORCH_FLICKER_AMOUNT = 5
TORCH_FLICKER_SPEED = 0.6


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


# =============================================================================
# SMALL UTILITY FUNCTIONS
# =============================================================================

def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def object_value(game_object, name: str, default=None):
    """Obtain a value from either an object instance or a dictionary."""

    if isinstance(game_object, dict):
        return game_object.get(name, default)

    return getattr(game_object, name, default)


def get_object_centre(game_object) -> tuple[float, float]:
    """Find an object's centre from a rect, or from x/y/width/height."""

    rectangle = object_value(game_object, "rect")

    if rectangle is not None:
        return float(rectangle.centerx), float(rectangle.centery)

    x = float(object_value(game_object, "x", 0))
    y = float(object_value(game_object, "y", 0))

    width = float(object_value(game_object, "width", 0))
    height = float(object_value(game_object, "height", 0))

    return x + width / 2, y + height / 2


# =============================================================================
# LIGHT COLLECTION
# =============================================================================

def collect_object_lights(
    game_objects: Iterable,
    time_seconds: float,
) -> list[LightSource]:
    """Turn player and torch objects into light sources."""

    lights: list[LightSource] = []

    for game_object in game_objects:
        object_number = object_value(
            game_object,
            "object_number",
            object_value(game_object, "type_code"),
        )

        x, y = get_object_centre(game_object)

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

    return lights


# =============================================================================
# DARKNESS AND LIGHT DRAWING
# =============================================================================

def cut_soft_light_from_darkness(
    darkness_surface: pygame.Surface,
    x: float,
    y: float,
    radius: float,
    strength: int,
) -> None:
    """Remove darkness around a light source via alpha subtraction."""

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
    """Draw a darkness overlay with lights cut out of it."""

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
    Stores lighting for one level.

    Create one instance when the level loads:

        effects = EnvironmentEffects(tile_map=level_map, tile_size=TILE_SIZE)
    """

    def __init__(
        self,
        tile_map: Sequence[Sequence[int]],
        tile_size: int = TILE_SIZE,
    ) -> None:
        self.tile_map = tile_map
        self.tile_size = tile_size

    def draw_lighting(
        self,
        screen: pygame.Surface,
        game_objects: Iterable,
        camera_x: float,
        camera_y: float,
        time_seconds: float,
    ) -> None:
        """Draw darkness with player and torch lights cut out."""

        object_lights = collect_object_lights(
            game_objects=game_objects,
            time_seconds=time_seconds,
        )

        draw_lighting(
            screen=screen,
            light_sources=object_lights,
            camera_x=camera_x,
            camera_y=camera_y,
        )
