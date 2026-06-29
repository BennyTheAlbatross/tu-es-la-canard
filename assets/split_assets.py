
from pathlib import Path
from PIL import Image
from collections import deque

SOURCE_IMAGE = "assets.png"
DOOR_SOURCE_IMAGE = "doors.png"
OUTPUT_DIR = Path("split_assets")

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


if __name__ == "__main__":
    main()
