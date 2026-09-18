import csv
import os
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from rules.gates import gate_allows
from tuer_le_canard.game_data import load_definitions, load_level


ROOT = Path(__file__).resolve().parents[1]


class GateRuleTests(unittest.TestCase):
    def test_each_arrow_allows_only_its_direction(self):
        directions = {
            "one_way_up": (0, -1),
            "one_way_right": (1, 0),
            "one_way_down": (0, 1),
            "one_way_left": (-1, 0),
        }
        for name, allowed in directions.items():
            with self.subTest(name=name):
                self.assertTrue(gate_allows(name, *allowed))
                self.assertFalse(gate_allows(name, -allowed[0], -allowed[1]))

    def test_diagonal_uses_dominant_axis(self):
        self.assertTrue(gate_allows("one_way_right", 4, 1))
        self.assertFalse(gate_allows("one_way_down", 4, 1))


class DataTests(unittest.TestCase):
    def test_new_object_ids_are_unique_and_present(self):
        definitions = load_definitions(ROOT / "rules/objects.csv")
        self.assertEqual(set(range(16, 21)), set(definitions).intersection(range(16, 21)))
        self.assertEqual("hidden_door", definitions[20].object_type)

    def test_every_map_loads_and_has_one_player(self):
        for map_path in sorted((ROOT / "maps/game").glob("*.csv")):
            with self.subTest(map=map_path.name):
                level = load_level(map_path, ROOT / "rules/objects.csv")
                self.assertIsNotNone(level.spawn)
                with map_path.open(encoding="utf-8-sig", newline="") as handle:
                    player_count = sum(cell.strip() == "9" for row in csv.reader(handle) for cell in row)
                self.assertEqual(1, player_count)


if __name__ == "__main__":
    unittest.main()
