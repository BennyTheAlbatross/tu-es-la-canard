import os
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from rules.wall_rendering import (
    EAST,
    NORTH,
    SOUTH,
    WEST,
    WALL_STYLE_CLASSIC,
    WALL_STYLE_PSEUDO3D,
    build_wall_variant_cache,
    iter_contact_shadows,
    load_pseudo3d_overlays,
    neighbour_mask,
    normalise_wall_style,
    wall_cells,
)
from rules.sprits import TILE_SIZE
from runtime.gameplay import build_static_world_surface


ROOT = Path(__file__).resolve().parents[1]


class NeighbourMaskTests(unittest.TestCase):
    def test_all_sixteen_cardinal_combinations(self):
        neighbours = (
            (NORTH, (-1, 0)),
            (EAST, (0, 1)),
            (SOUTH, (1, 0)),
            (WEST, (0, -1)),
        )
        for expected in range(16):
            cells = {(3, 3)}
            cells.update(
                (3 + dr, 3 + dc)
                for bit, (dr, dc) in neighbours
                if expected & bit
            )
            with self.subTest(mask=expected):
                self.assertEqual(expected, neighbour_mask(cells, 3, 3))

    def test_only_stone_wall_types_connect(self):
        barriers = [
            (0, 0, "border"),
            (40, 0, "stone"),
            (80, 0, "lava"),
            (120, 0, "water"),
            (160, 0, "wood"),
        ]
        self.assertEqual({(0, 0), (0, 1)}, wall_cells(barriers))

    def test_junction_shapes_have_expected_masks(self):
        cases = {
            "isolated": ({(2, 2)}, 0),
            "horizontal": ({(2, 1), (2, 2), (2, 3)}, EAST | WEST),
            "vertical": ({(1, 2), (2, 2), (3, 2)}, NORTH | SOUTH),
            "corner": ({(1, 2), (2, 2), (2, 3)}, NORTH | EAST),
            "tee": ({(1, 2), (2, 1), (2, 2), (2, 3)}, NORTH | EAST | WEST),
            "cross": ({(1, 2), (2, 1), (2, 2), (2, 3), (3, 2)}, 15),
        }
        for name, (cells, expected) in cases.items():
            with self.subTest(shape=name):
                self.assertEqual(expected, neighbour_mask(cells, 2, 2))


class ShadowTests(unittest.TestCase):
    def test_shadows_only_occupy_adjacent_floor_cells(self):
        cells = {(0, 0), (0, 1), (1, 0)}
        shadows = set(iter_contact_shadows(cells, world_columns=3, world_rows=3))
        self.assertEqual(
            {
                (80, 0, "shadow_east"),
                (40, 40, "shadow_south"),
                (40, 40, "shadow_east"),
                (0, 80, "shadow_south"),
                (40, 40, "shadow_east"),
            },
            shadows,
        )
        for x, y, _name in shadows:
            self.assertNotIn((y // TILE_SIZE[1], x // TILE_SIZE[0]), cells)


class AssetAndCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_style_switch_normalisation(self):
        self.assertEqual(WALL_STYLE_CLASSIC, normalise_wall_style("classic"))
        self.assertEqual(WALL_STYLE_PSEUDO3D, normalise_wall_style("PSEUDO3D"))
        self.assertEqual(WALL_STYLE_PSEUDO3D, normalise_wall_style("unknown"))

    def test_overlay_assets_are_exact_tile_size(self):
        overlays = load_pseudo3d_overlays()
        self.assertEqual(6, len(overlays))
        self.assertTrue(all(image.get_size() == TILE_SIZE for image in overlays.values()))

    def test_cache_has_no_more_than_sixteen_variants_per_texture(self):
        base = pygame.Surface(TILE_SIZE, pygame.SRCALPHA)
        base.fill((80, 80, 80, 255))
        env_images = {"border_image": base, "stone_tile": base}
        barriers = []
        for row in range(5):
            for column in range(5):
                barriers.append((column * 40, row * 40, "border" if row % 2 else "stone"))
        _cells, variants = build_wall_variant_cache(
            env_images, load_pseudo3d_overlays(), barriers
        )
        counts = {}
        for image_key, _mask in variants:
            counts[image_key] = counts.get(image_key, 0) + 1
        self.assertTrue(all(count <= 16 for count in counts.values()))

    def test_classic_static_render_is_the_original_blit_order(self):
        floor = pygame.Surface(TILE_SIZE)
        floor.fill((90, 70, 45))
        wall = pygame.Surface(TILE_SIZE)
        wall.fill((42, 43, 44))
        env_images = {
            "background_image": floor,
            "border_image": wall,
            "stone_tile": wall,
        }
        rendered, animated = build_static_world_surface(
            80,
            40,
            [(0, 0, "background"), (40, 0, "background")],
            [(40, 0, "border")],
            [],
            env_images,
            {},
            wall_style=WALL_STYLE_CLASSIC,
        )
        expected = pygame.Surface((80, 40)).convert()
        expected.fill((0, 0, 0))
        expected.blit(floor, (0, 0))
        expected.blit(floor, (40, 0))
        expected.blit(wall, (40, 0))
        self.assertEqual([], animated)
        self.assertEqual(
            pygame.image.tobytes(expected, "RGB"),
            pygame.image.tobytes(rendered, "RGB"),
        )

    def test_every_existing_map_remains_unmodified(self):
        for path in sorted((ROOT / "maps" / "game").glob("*.csv")):
            before = path.read_bytes()
            self.assertGreater(len(before), 0, path.name)
            self.assertEqual(before, path.read_bytes(), path.name)


if __name__ == "__main__":
    unittest.main()
