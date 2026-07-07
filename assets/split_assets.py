
from pathlib import Path
from PIL import Image
from collections import deque

SOURCE_IMAGE = "assets.png"
DOOR_SOURCE_IMAGE = "doors.png"
WALL_SOURCE_IMAGE = "walls.png"
MORE_WALLS_SOURCE_IMAGE = "more_walls.png"
TORCH_SOURCE_IMAGE = "torch/torch_sheet.png"
ROCK_ENEMY_SOURCE_IMAGE = "rock_enemy/up-down-left-right.png"
OUTPUT_DIR = Path("split_assets")

# walls.png is a 5x5 grid. Columns have uneven widths (full walls vs. narrow
# edge/pillar pieces) so we crop by explicit cell bands and trim the black
# padding per cell. Bands are (start, end) pixel boundaries including gutters.
WALL_COL_BANDS = [(0, 291), (291, 475), (475, 651), (651, 958), (958, 1254)]
WALL_ROW_BANDS = [(0, 258), (258, 499), (499, 739), (739, 979), (979, 1254)]
WALL_MATERIALS = ["brick", "cobble", "sandstone", "lava", "mossy"]
WALL_VARIANTS = ["full", "left", "pillar", "block", "right"]

# more_walls.png is a 2-row (lava, mossy) sheet of room-border pieces. Columns:
# a top edge, three vertical-edge pillars, a top corner, a bottom edge and a
# bottom corner. Crops are content-tight (no trim) so solid tiles fill their
# cell edge-to-edge with no black border.
MORE_WALLS_ROW_BANDS = [(181, 439), (556, 816)]  # lava, mossy
MORE_WALLS_MATERIALS = ["lava", "mossy"]
# (name, left, right) for each column tile within a row.
MORE_WALLS_COLS = [
    ("top", 26, 270),
    ("vertical_1", 324, 387),
    ("vertical_2", 416, 478),
    ("vertical_3", 507, 570),
    ("corner_top", 626, 882),
    ("bottom", 942, 1200),
    ("corner_bottom", 1262, 1499),
]

# torch/torch_sheet.png is a 2-row (red, green) x 6-frame animation sheet. Each
# frame is a full wall tile with the animated flame. Crops are content-tight so
# each frame fills its tile with no black border.
TORCH_OUTPUT_DIR = Path("torch")
TORCH_ROW_BANDS = [(137, 500), (517, 887)]  # red, green
TORCH_COLORS = ["red", "green"]
TORCH_COL_BANDS = [
    (32, 263), (278, 510), (525, 758), (772, 1004), (1019, 1251), (1265, 1498),
]

# rock_enemy/up-down-left-right.png is a 4-row animation sheet.
# Rows are: up, down, left, right. We split each row into 8 frames.
ROCK_ENEMY_OUTPUT_DIR = Path("rock_enemy")
ROCK_ENEMY_DIRECTIONS = ["up", "down", "left", "right"]
ROCK_ENEMY_ROW_BANDS = [(0, 76), (76, 152), (152, 228), (228, 304)]
ROCK_ENEMY_COL_BANDS = [(0, 96), (96, 192), (192, 288), (288, 384), (384, 480), (480, 576), (576, 672), (672, 768)]

# Approximate crop rectangles from the generated sheet:
# (left, top, right, bottom)
SPRITES = {
    # Character poses
    "duck_front":      (35,  70,  210, 380),
    "duck_side":       (235, 75,  430, 380),
    "duck_profile":    (485, 75,  650, 380),
    "duck_back_3q":    (690, 90,  850, 380),
    "duck_back":       (845, 90, 1010, 380),

    # Walk cycle
    "duck_walk_1":     (35,  440, 220, 690),
    "duck_walk_2":     (245, 440, 430, 690),
    "duck_walk_3":     (455, 440, 650, 690),
    "duck_walk_4":     (655, 440, 860, 690),
    "duck_jump":       (900, 405, 1080, 685),

    # Gems
    "gem_green":       (1075, 165, 1235, 390),
    "gem_red":         (1075, 430, 1235, 690),

    # Top row textures
    "tile_grass":      (30,  775, 260, 980),
    "tile_dirt":       (270, 775, 500, 980),
    "tile_stone":      (510, 775, 745, 980),
    "tile_wood":       (750, 775, 985, 980),
    "tile_brick":      (995, 775, 1230, 980),

    # Bottom row textures
    "tile_water":      (30,  995, 260, 1185),
    "tile_sand":       (270, 995, 500, 1185),
    "tile_cave":       (510, 995, 745, 1185),
    "tile_lava":       (750, 995, 985, 1185),
    "tile_metal":      (995, 995, 1230, 1185),
}


def trim_black(im, threshold=10, padding=2):
    """
    Remove black background around a sprite/tile.
    threshold: pixels darker than this are treated as background.
    padding: extra pixels kept around the detected content.
    """
    rgba = im.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size

    xs = []
    ys = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0 and (r > threshold or g > threshold or b > threshold):
                xs.append(x)
                ys.append(y)

    if not xs or not ys:
        return rgba

    left = max(0, min(xs) - padding)
    top = max(0, min(ys) - padding)
    right = min(w, max(xs) + 1 + padding)
    bottom = min(h, max(ys) + 1 + padding)

    return rgba.crop((left, top, right, bottom))


def trim_background(im, threshold=25, padding=2):
    """Trim a uniform background color around a sprite/tile."""
    rgba = im.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    bg_r, bg_g, bg_b, _bg_a = px[0, 0]

    xs = []
    ys = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0 and abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b) > threshold:
                xs.append(x)
                ys.append(y)

    if not xs or not ys:
        return rgba

    left = max(0, min(xs) - padding)
    top = max(0, min(ys) - padding)
    right = min(w, max(xs) + 1 + padding)
    bottom = min(h, max(ys) + 1 + padding)

    return rgba.crop((left, top, right, bottom))


def _find_components(im, threshold=10, min_area=3000):
    """Return bounding boxes for non-black connected components."""
    rgba = im.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    visited = bytearray(w * h)
    boxes = []

    for y in range(h):
        for x in range(w):
            idx = y * w + x
            if visited[idx]:
                continue

            r, g, b, a = px[x, y]
            if a == 0 or (r <= threshold and g <= threshold and b <= threshold):
                visited[idx] = 1
                continue

            queue = deque([(x, y)])
            visited[idx] = 1
            min_x = max_x = x
            min_y = max_y = y
            area = 0

            while queue:
                cx, cy = queue.popleft()
                area += 1
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)

                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if nx < 0 or ny < 0 or nx >= w or ny >= h:
                        continue
                    nidx = ny * w + nx
                    if visited[nidx]:
                        continue

                    rr, gg, bb, aa = px[nx, ny]
                    if aa == 0 or (rr <= threshold and gg <= threshold and bb <= threshold):
                        visited[nidx] = 1
                        continue

                    visited[nidx] = 1
                    queue.append((nx, ny))

            if area >= min_area:
                boxes.append((min_x, min_y, max_x + 1, max_y + 1, area))

    return boxes


def split_doors():
    """Split doors.png into parts and write door_closed/door_open aliases."""
    source = Path(DOOR_SOURCE_IMAGE)
    if not source.exists():
        print(f"Skipped door split: {DOOR_SOURCE_IMAGE!r} not found")
        return

    image = Image.open(source).convert("RGBA")
    boxes = _find_components(image, threshold=10, min_area=3000)
    if not boxes:
        print("No large door components found in doors.png")
        return

    # Stable ordering for predictable filenames.
    boxes.sort(key=lambda b: (b[1], b[0]))
    parts = []
    for idx, (left, top, right, bottom, _area) in enumerate(boxes, start=1):
        cropped = image.crop((left, top, right, bottom))
        trimmed = trim_black(cropped)
        out_path = Path(f"door_part_{idx:02d}.png")
        trimmed.save(out_path)
        parts.append(out_path)
        print(f"Saved {out_path}")

    # Use the first two parts as gameplay aliases.
    if parts:
        Image.open(parts[0]).save("door_closed.png")
        print("Saved door_closed.png")
    if len(parts) > 1:
        Image.open(parts[1]).save("door_open.png")
        print("Saved door_open.png")
    elif parts:
        Image.open(parts[0]).save("door_open.png")
        print("Saved door_open.png (fallback copy of closed)")


def split_walls():
    """Split walls.png into a 5x5 grid of individual wall tiles."""
    source = Path(WALL_SOURCE_IMAGE)
    if not source.exists():
        print(f"Skipped wall split: {WALL_SOURCE_IMAGE!r} not found")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)
    image = Image.open(source).convert("RGBA")

    for row, (top, bottom) in enumerate(WALL_ROW_BANDS):
        material = WALL_MATERIALS[row]
        for col, (left, right) in enumerate(WALL_COL_BANDS):
            variant = WALL_VARIANTS[col]
            cropped = image.crop((left, top, right, bottom))
            trimmed = trim_black(cropped)

            out_path = OUTPUT_DIR / f"wall_{material}_{variant}.png"
            trimmed.save(out_path)
            print(f"Saved {out_path}")


def split_more_walls():
    """Split more_walls.png into lava/mossy room-border edge and corner tiles."""
    source = Path(MORE_WALLS_SOURCE_IMAGE)
    if not source.exists():
        print(f"Skipped more-wall split: {MORE_WALLS_SOURCE_IMAGE!r} not found")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)
    image = Image.open(source).convert("RGBA")

    for row, (top, bottom) in enumerate(MORE_WALLS_ROW_BANDS):
        material = MORE_WALLS_MATERIALS[row]
        for variant, left, right in MORE_WALLS_COLS:
            cell = image.crop((left, top, right, bottom))
            out_path = OUTPUT_DIR / f"wall_{material}_{variant}.png"
            cell.save(out_path)
            print(f"Saved {out_path}")


def split_torch():
    """Split torch/torch_sheet.png into red/green 6-frame animation tiles."""
    source = Path(TORCH_SOURCE_IMAGE)
    if not source.exists():
        print(f"Skipped torch split: {TORCH_SOURCE_IMAGE!r} not found")
        return

    TORCH_OUTPUT_DIR.mkdir(exist_ok=True)
    image = Image.open(source).convert("RGBA")

    for row, (top, bottom) in enumerate(TORCH_ROW_BANDS):
        color = TORCH_COLORS[row]
        for frame, (left, right) in enumerate(TORCH_COL_BANDS, start=1):
            cell = image.crop((left, top, right, bottom))
            out_path = TORCH_OUTPUT_DIR / f"torch_{color}_{frame}.png"
            cell.save(out_path)
            print(f"Saved {out_path}")


def split_rock_enemy():
    """Split the rock enemy sheet into directional animation frames."""
    source = Path(ROCK_ENEMY_SOURCE_IMAGE)
    if not source.exists():
        print(f"Skipped rock enemy split: {ROCK_ENEMY_SOURCE_IMAGE!r} not found")
        return

    ROCK_ENEMY_OUTPUT_DIR.mkdir(exist_ok=True)
    image = Image.open(source).convert("RGBA")

    for row, (top, bottom) in enumerate(ROCK_ENEMY_ROW_BANDS):
        direction = ROCK_ENEMY_DIRECTIONS[row]
        for frame, (left, right) in enumerate(ROCK_ENEMY_COL_BANDS, start=1):
            cropped = image.crop((left, top, right, bottom))
            trimmed = trim_background(cropped, threshold=25, padding=2)
            out_path = ROCK_ENEMY_OUTPUT_DIR / f"rock_{direction}_{frame}.png"
            trimmed.save(out_path)
            print(f"Saved {out_path}")


def main():
    source = Path(SOURCE_IMAGE)
    if not source.exists():
        raise FileNotFoundError(
            f"Could not find {SOURCE_IMAGE!r}. Put this script in the same folder as the image, "
            "or change SOURCE_IMAGE to the correct path."
        )

    OUTPUT_DIR.mkdir(exist_ok=True)
    image = Image.open(source).convert("RGBA")

    for name, box in SPRITES.items():
        cropped = image.crop(box)
        trimmed = trim_black(cropped)

        out_path = OUTPUT_DIR / f"{name}.png"
        trimmed.save(out_path)
        print(f"Saved {out_path}")

    print(f"\nDone. Assets saved to: {OUTPUT_DIR.resolve()}")

    # Also split door assets if doors.png exists.
    split_doors()

    # Also split wall assets if walls.png exists.
    split_walls()

    # Also split the extra room-border wall pieces if more_walls.png exists.
    split_more_walls()

    # Also split the animated torch frames if torch_sheet.png exists.
    split_torch()

    # Also split the rock enemy sheet into directional animation frames.
    split_rock_enemy()


if __name__ == "__main__":
    main()
