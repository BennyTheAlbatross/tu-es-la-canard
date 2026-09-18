import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ObjectDefinition:
    number: int
    name: str
    object_type: str
    solid: bool
    kills_player: bool
    movement: str
    ability_rule: str


@dataclass
class MapObject:
    definition: ObjectDefinition
    x: float
    y: float
    active: bool = True
    direction: int = 1


@dataclass
class Level:
    grid: list[list[int]]
    definitions: dict[int, ObjectDefinition]
    objects: list[MapObject]
    spawn: tuple[float, float]

    @property
    def width(self):
        return len(self.grid[0])

    @property
    def height(self):
        return len(self.grid)

    def definition_at(self, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None
        return self.definitions.get(self.grid[y][x])


def load_definitions(path):
    definitions = {}
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            number = int(row["object_number"])
            definitions[number] = ObjectDefinition(
                number=number,
                name=row["object_name"].strip(),
                object_type=row["object_type"].strip(),
                solid=row["solid"].strip().lower() == "yes",
                kills_player=row["kills_player"].strip().lower() == "yes",
                movement=row["movement"].strip(),
                ability_rule=row["ability_rule"].strip(),
            )
    return definitions


def load_level(map_path, objects_path):
    definitions = load_definitions(objects_path)
    rows = []
    with Path(map_path).open(encoding="utf-8-sig", newline="") as handle:
        for raw_row in csv.reader(handle):
            row = []
            for cell in raw_row:
                cell = cell.strip()
                row.append(int(cell) if cell else 0)
            rows.append(row)

    width = max(len(row) for row in rows)
    grid = [row + [0] * (width - len(row)) for row in rows]
    objects = []
    spawn = None

    for row_index, row in enumerate(grid):
        for column_index, object_number in enumerate(row):
            definition = definitions.get(object_number)
            if definition is None:
                continue
            x = column_index + 0.5
            y = row_index + 0.5
            if definition.object_type == "player":
                spawn = (x, y)
                grid[row_index][column_index] = 0
            elif definition.object_type in {"enemy", "gem", "decoration", "door"}:
                objects.append(MapObject(definition, x, y))
                if definition.object_type != "door":
                    grid[row_index][column_index] = 0

    if spawn is None:
        raise ValueError("The map contains no player object")

    return Level(grid, definitions, objects, spawn)
