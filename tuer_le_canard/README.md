# Tuer le canard

A minimal first-person ray-cast experiment based on the maps, object rules, and artwork from **Tu es la canard**.

Keep this directory beside the original project:

```text
Documents/
├── tu-es-la-canard/
└── tuer_le_canard/
```

## Run

```bash
python3 main.py
```

Requires Python 3 and Pygame 2.

## Controls

- `W` / `Up`: move forward
- `S` / `Down`: move backward
- `A` / `D`: strafe
- `Left` / `Right`: turn
- `Mouse`: turn
- `-` / `+`: lower or raise internal rendering quality
- `F11`: toggle fullscreen
- `Escape`: quit

## Current scope

- Loads `../tu-es-la-canard/maps/game/map1.csv` directly, without changing its format.
- Loads object meaning directly from `../tu-es-la-canard/rules/objects.csv`.
- Loads the original wall, enemy, gem, door, and torch artwork directly from the original project.
- Renders barrier tiles as textured ray-cast walls.
- Renders enemies, gems, and torches as billboards.
- Collecting every gem opens the exit door.
- Imports enemy movement and collision intent from the original `objects.csv`: fire and water patrol horizontally, while rock patrols vertically.
- Uses a 1280×720 window with a lower-resolution retro render surface.
- Caches shaded wall strips and scaled sprites to avoid repeating expensive transforms every frame.

Maps, object rules, and assets are not duplicated. Changes to those shared files are immediately available to both games. The new project contains only ray-casting-specific code.
