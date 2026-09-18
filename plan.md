# Collapsing Wooden Floor Plan

## Purpose

Add one new environmental puzzle mechanic: a wooden bridge tile that begins to fail when the duck steps on it. The tile warns the player, collapses after a short delay, becomes lethal while missing, and later rebuilds itself so the level cannot become permanently unwinnable.

This plan deliberately excludes the player-controlled torch, enemy tracking, cutscenes, scoring, and level redesign. The goal is to implement and test one complete mechanic without expanding the rest of the game.

## Player Experience

The tile should communicate its behavior visually without explanatory UI:

1. It initially resembles a normal wooden floor or bridge.
2. The first time the duck steps on it, the wood shifts and begins to wobble.
3. Cracks become severe shortly before the collapse.
4. The floor falls away and leaves a dark hole.
5. If the duck overlaps the tile when it collapses, or walks onto it while it is collapsed, the duck dies.
6. After a short delay, the bridge returns to its same intact state.

The timer continues after the duck leaves the tile. This is important: triggering a bridge should create a committed decision rather than allowing the player to reset it by stepping off and on repeatedly.

## Recommended Timing

Start with these values and tune them after playing a small test room:

| Phase | Duration | Meaning |
| --- | ---: | --- |
| Intact | Unlimited | Safe until first touched |
| Wobble | 0.65 seconds | Early warning; plenty of time to react |
| Cracked | 0.45 seconds | Urgent final warning |
| Collapsed | 3.0 seconds | Missing floor and lethal area |

The complete warning lasts 1.10 seconds. A player moving at the current speed should be able to cross one tile comfortably, while a row of several tiles creates pressure.

## State Model

Each placed collapsing tile needs independent state. It should therefore be represented by an object rather than the tuple format currently used for ordinary background and barrier tiles.

Use four explicit states:

```text
INTACT -> WOBBLE -> CRACKED -> COLLAPSED -> INTACT
```

Suggested instance data:

```python
rect
state
state_elapsed
wobble_duration
cracked_duration
collapsed_duration
```

Suggested responsibilities:

```python
trigger()
update(delta_seconds)
is_collapsed
is_lethal
current_image
```

`trigger()` only changes `INTACT` to `WOBBLE`. Calling it during any later state does nothing. `update()` adds real elapsed time and performs state transitions. Returning to `INTACT` resets `state_elapsed` to zero.

## Per-Frame Gameplay Loop

The mechanic should run in this order inside the gameplay loop:

```text
1. Calculate delta_seconds for this frame.
2. Read input and move the player.
3. Resolve normal barriers.
4. Check whether the player touches an intact collapsing floor; trigger it.
5. Update every collapsing floor timer.
6. Check whether the player overlaps a collapsed floor; return "dead" if so.
7. Process enemies, gems, and the exit as normal.
8. Draw each collapsing floor using the image for its current state.
```

Updating before the lethal check means the exact frame that changes to `COLLAPSED` can kill the player. Triggering before updating is also safe as long as only the current frame's small `delta_seconds` is added.

## Required Changes by File

### `rules/objects.csv`

Add a new object definition using the next available object number, currently `15`:

```text
15,collapsing_floor,15,hazard,collapsing_floor,no,no,yes,collapse_delay:1.1,
```

The important field is `object_type=hazard`. `build_world()` can route all objects of this type into a dedicated hazards collection. The duration can initially remain a Python constant; the `ability_rule` value records the intended rule and can become configurable later if useful.

Do not reuse object `12` (`wood`). Ordinary wood remains a solid barrier, while the new bridge is traversable and stateful.

### `rules/hazards.py` (new)

Create a small module containing `CollapsingFloor` and its state constants. Keeping this behavior outside `interactions.py` prevents that file becoming a collection of unrelated special cases.

The class should:

- Create a tile-sized `pygame.Rect` from its map coordinates.
- Store elapsed time as seconds, not frames.
- Expose `trigger()` and `update(delta_seconds)`.
- Select one of the four loaded images from its current state.
- Report lethal status only while `COLLAPSED`.
- Contain no drawing, camera, menu, or player-death behavior.

The class owns state; the gameplay loop owns interaction order and decides when the player dies.

### `rules/sprits.py`

Add `load_collapsing_floor_images()` alongside the existing image loader functions. Load and scale these files to `TILE_SIZE`:

- `assets/collapsing_floor_intact.png`
- `assets/collapsing_floor_wobble.png`
- `assets/collapsing_floor_cracked.png`
- `assets/collapsing_floor_collapsed.png`

Return a dictionary keyed by the same state names used by `CollapsingFloor`. Centralizing loading here follows the project's current asset pattern and ensures images are loaded once when a level starts, not once per tile or frame.

### `runtime/gameplay.py`: world construction

In `build_world()`:

- Add a `collapsing_floors` list.
- When `object_type == 'hazard'` and the name is `collapsing_floor`, create one `CollapsingFloor` at that cell.
- Do not add the tile to `background`, `barriers`, or `animated_tiles`.
- Return the new list with the other world collections.

Not adding it to the pre-rendered static surface is essential. A stateful tile must be redrawn each frame so its image can change.

### `runtime/gameplay.py`: timing

At the start of each gameplay session, create a local `pygame.time.Clock()`. At the beginning of each loop iteration, obtain:

```python
delta_seconds = clock.tick(FPS) / 1000.0
```

Use `delta_seconds` for collapsing-floor updates. This makes the collapse delay independent of frame rate and map size.

This mechanic does not require converting all existing movement to delta time in the same change. That broader timing cleanup is still desirable, but the collapsing-floor timer itself must be time-based from the start.

### `runtime/gameplay.py`: interaction

After player movement and barrier resolution:

```python
for floor in collapsing_floors:
    if floor.rect.colliderect(player.rect):
        floor.trigger()

for floor in collapsing_floors:
    floor.update(delta_seconds)

for floor in collapsing_floors:
    if floor.is_lethal and floor.rect.colliderect(player.rect):
        return 'dead'
```

Keep this separate from `interactions.enemy()`. Both produce death, but they are different rules and should remain easy to reason about.

Use rectangle overlap initially. If the tile triggers too easily when the duck barely clips a corner, later use the player's center point or a smaller inset trigger rectangle. Do not add that complexity before playtesting.

### `runtime/gameplay.py`: drawing

Add `collapsing_floors` to `draw_world()`. Draw them after the static world and animated lava, but before gems, enemies, and the player. For each visible floor:

```python
screen.blit(
    floor.current_image,
    (floor.rect.x - camera_x, floor.rect.y - camera_y),
)
```

Apply the same camera visibility check already used for animated tiles and other dynamic objects.

The collapsed image remains visible as a dark hole. It should not disappear completely because the player needs a clear visual explanation for the lethal space.

### `maps/game/` and `maps/source/`

Do not immediately revise every level. First add object ID `15` to a copy or a deliberately small test section of one map.

A useful first test room contains:

- One isolated collapsing tile with safe floor around it.
- A two-tile bridge where both tiles trigger separately.
- A three-to-five-tile bridge that tests whether the warning duration feels fair.
- Safe ground on both ends so the mechanic can be tested repeatedly.

Once behavior is stable, update the corresponding `.ods` source map before treating the CSV as final. The spreadsheet should remain the editable source of truth.

## Asset Set

The four generated PNGs intentionally follow the existing warm-brown, top-down pixel-art wood style:

| File | State | Visual job |
| --- | --- | --- |
| `collapsing_floor_intact.png` | `INTACT` | Blend with existing wooden areas |
| `collapsing_floor_wobble.png` | `WOBBLE` | Show shifted boards and early cracks |
| `collapsing_floor_cracked.png` | `CRACKED` | Give a strong final warning |
| `collapsing_floor_collapsed.png` | `COLLAPSED` | Clearly show a lethal empty opening |

The project currently scales source art to `40 x 40` at load time, so these source PNGs can follow the same workflow as the existing mixed-resolution assets. Use nearest-neighbor scaling if the default Pygame scaling softens the pixel edges.

## Decisions for the First Version

- Each tile acts independently, even when several tiles form one bridge.
- Stepping off does not cancel or reset the collapse countdown.
- A collapsed tile kills on contact; it is not a solid wall.
- The tile automatically respawns after three seconds.
- Enemies do not trigger the bridge and are not killed by it.
- Gems and other objects should not be placed on the same map cell.
- No particles, sound effects, camera shake, or configurable bridge groups are required initially.

These limits keep the first implementation small while leaving clear extension points.

## Test Checklist

### State behavior

- An untouched tile remains intact indefinitely.
- First contact triggers it exactly once.
- Leaving the tile does not stop the countdown.
- The visual states appear in the correct order.
- The tile collapses after the same real-world duration at different frame rates.
- The tile returns after the collapsed duration.

### Player interaction

- Standing on the tile at collapse returns the normal death result.
- Entering an already collapsed tile also kills the player.
- Crossing before collapse is safe.
- Touching only a neighboring tile does not trigger it.
- Multiple bridge tiles maintain independent timers.

### Rendering and maps

- The tile is drawn in the correct world position while the camera moves.
- The duck and enemies render above it.
- The collapsed hole remains visible under the darkness shader.
- Map object `15` loads without affecting existing map IDs.
- Existing levels containing no collapsing floors behave unchanged.

## Later Extensions, Not Part of This Change

Only consider these after the basic tile is fun and reliable:

- A sound during wobble and a snap on collapse.
- Small debris particles.
- Permanent-collapse variants.
- Linked bridge groups that collapse together.
- Floors triggered by enemies or movable objects.
- Different timing values encoded in map metadata.

The first implementation should remain one tile type, four states, one timer loop, and one clear death rule.
