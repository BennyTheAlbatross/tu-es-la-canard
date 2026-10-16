# Pseudo-3D wall rendering

The enhanced wall style is a 2D-only presentation layer. It does not change CSV
coordinates, collision rectangles, tile dimensions, camera perspective, or the
first-person raycaster.

## Architecture

- `rules/wall_rendering.py` identifies connected `border` and `stone` cells,
  encodes their north/east/south/west neighbours as a four-bit mask, and builds
  only the texture/mask variants used by the loaded map.
- `runtime/gameplay.py` adds the cached variants and floor contact shadows while
  it builds the existing static world surface. No texture generation or
  per-pixel work occurs in the frame loop.
- `assets/tiles/walls_pseudo3d/` contains transparent, tile-sized overlays. The
  original `tile_cave.png` and `tile_stone.png` remain the base artwork.
- The existing lighting pass is applied after all scene rendering, so torches
  illuminate the enhanced surfaces once, in the same way as classic walls.

The neighbour bits are `N=1`, `E=2`, `S=4`, and `W=8`, covering all 16 possible
isolated, segment, corner, T-junction, cross-junction, and solid-mass cases.
Water, lava, wood, gates, objects and sprites keep their prior rendering.

## Selecting a style

Pseudo-3D is the default for a normal 2D launch. Press `V` while playing to
switch styles; this rebuilds the static surface once. For launch configuration:

```bash
CANARD_WALL_STYLE=classic python3 runtime/main_menu.py
CANARD_WALL_STYLE=pseudo3d python3 runtime/main_menu.py
```

Code that calls `runtime.gameplay.main()` may pass `wall_style="classic"` or
`wall_style="pseudo3d"` explicitly.

## Rebuilding assets and screenshots

The overlay generator uses Pygame drawing primitives and preserves hard pixel
edges. It does not read or overwrite the original textures:

```bash
python3 scripts/generate_pseudo3d_wall_overlays.py
python3 scripts/capture_wall_style_comparison.py
```

The capture script renders both styles from `map5.csv` with the same player,
camera, object state, light state, and timestamp. It writes the comparison images
referenced by the README.

## Verification

Run:

```bash
python3 -m unittest discover -s tests -v
```

`tests/test_wall_rendering.py` covers every neighbour mask, representative wall
segments and junctions, supported wall types, contact-shadow placement, asset
dimensions, cache bounds, style selection, and map-file preservation. Existing
mechanics/map tests continue to cover CSV compatibility. The raycaster has no
imports from the pseudo-3D module and continues loading its original wall assets.
