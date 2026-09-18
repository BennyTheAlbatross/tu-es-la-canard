import math
from pathlib import Path

import pygame

from game_data import load_level


ROOT = Path(__file__).resolve().parent
SOURCE_PROJECT = ROOT.parent / "tu-es-la-canard"
SCREEN_SIZE = (1280, 720)
RENDER_SIZES = ((400, 225), (480, 270), (640, 360))
DEFAULT_RENDER_QUALITY = 1
FOV = math.radians(66)
MOVE_SPEED = 2.8
TURN_SPEED = 2.0
MOUSE_SENSITIVITY = 0.0025
PLAYER_RADIUS = 0.18
MAX_VIEW_DISTANCE = 20.0
ENEMY_SPEEDS = {
    "enemy_fire": 1.8,
    "enemy_water": 1.2,
    "enemy_rock": 0.7,
}

WALL_ASSETS = {
    "border": "tile_cave.png",
    "lava": "lava_1.png",
    "water": "tile_water.png",
    "stone": "tile_stone.png",
    "wood": "tile_wood.png",
    "end_door": "doorClosed.png",
}

SPRITE_ASSETS = {
    "enemy_fire": "enemy_fire.png",
    "enemy_water": "enemy_water.png",
    "enemy_rock": "enemy_rock.png",
    "gem_emerald": "gem_green.png",
    "gem_ruby": "gem_red.png",
    "gem_sapphire": "gem_red.png",
    "torch": "torch/torch_red_1.png",
}


def load_image(relative_path):
    image = pygame.image.load(SOURCE_PROJECT / "assets" / relative_path).convert_alpha()
    image.set_colorkey((0, 0, 0))
    return image


def load_assets():
    walls = {
        name: pygame.transform.scale(load_image(path).convert(), (128, 128))
        for name, path in WALL_ASSETS.items()
    }
    sprites = {name: load_image(path) for name, path in SPRITE_ASSETS.items()}
    return walls, sprites


def door_is_open(level):
    return not any(
        obj.active and obj.definition.object_type == "gem"
        for obj in level.objects
    )


def cell_blocks(level, map_x, map_y):
    definition = level.definition_at(map_x, map_y)
    if definition is None:
        return True
    if definition.object_type == "door":
        return not door_is_open(level)
    return definition.object_type == "barrier" or definition.solid


def can_stand(level, x, y):
    for offset_x, offset_y in (
        (-PLAYER_RADIUS, -PLAYER_RADIUS),
        (PLAYER_RADIUS, -PLAYER_RADIUS),
        (-PLAYER_RADIUS, PLAYER_RADIUS),
        (PLAYER_RADIUS, PLAYER_RADIUS),
    ):
        if cell_blocks(level, int(x + offset_x), int(y + offset_y)):
            return False
    return True


def move_player(level, position, direction, delta_seconds, keys):
    forward = float(keys[pygame.K_w] or keys[pygame.K_UP]) - float(keys[pygame.K_s] or keys[pygame.K_DOWN])
    strafe = float(keys[pygame.K_d]) - float(keys[pygame.K_a])
    length = math.hypot(forward, strafe)
    if length > 1.0:
        forward /= length
        strafe /= length

    direction_x, direction_y = math.cos(direction), math.sin(direction)
    right_x, right_y = -direction_y, direction_x
    distance = MOVE_SPEED * delta_seconds
    target_x = position[0] + (direction_x * forward + right_x * strafe) * distance
    target_y = position[1] + (direction_y * forward + right_y * strafe) * distance

    if can_stand(level, target_x, position[1]):
        position[0] = target_x
    if can_stand(level, position[0], target_y):
        position[1] = target_y


def enemy_blocked_by(level, enemy, x, y):
    definition = level.definition_at(int(x), int(y))
    if definition is None:
        return True
    rule = enemy.definition.ability_rule
    if not rule.startswith("blocks:"):
        return False
    blocked_names = {name.strip() for name in rule.split(":", 1)[1].split("|")}
    return definition.name in blocked_names


def update_enemies(level, delta_seconds):
    for enemy in level.objects:
        if (
            not enemy.active
            or enemy.definition.object_type != "enemy"
            or enemy.definition.movement != "enemy_movement"
        ):
            continue

        speed = ENEMY_SPEEDS.get(enemy.definition.name, 1.0)
        distance = speed * delta_seconds * enemy.direction
        if enemy.definition.name == "enemy_rock":
            target_x, target_y = enemy.x, enemy.y + distance
        else:
            target_x, target_y = enemy.x + distance, enemy.y

        if enemy_blocked_by(level, enemy, target_x, target_y):
            enemy.direction *= -1
        else:
            enemy.x = target_x
            enemy.y = target_y


def cast_ray(level, player_x, player_y, ray_direction_x, ray_direction_y):
    map_x, map_y = int(player_x), int(player_y)
    delta_x = abs(1.0 / ray_direction_x) if ray_direction_x else 1e30
    delta_y = abs(1.0 / ray_direction_y) if ray_direction_y else 1e30

    if ray_direction_x < 0:
        step_x = -1
        side_distance_x = (player_x - map_x) * delta_x
    else:
        step_x = 1
        side_distance_x = (map_x + 1.0 - player_x) * delta_x

    if ray_direction_y < 0:
        step_y = -1
        side_distance_y = (player_y - map_y) * delta_y
    else:
        step_y = 1
        side_distance_y = (map_y + 1.0 - player_y) * delta_y

    side = 0
    for _ in range(128):
        if side_distance_x < side_distance_y:
            side_distance_x += delta_x
            map_x += step_x
            side = 0
        else:
            side_distance_y += delta_y
            map_y += step_y
            side = 1

        if cell_blocks(level, map_x, map_y):
            break

    if side == 0:
        distance = (map_x - player_x + (1 - step_x) / 2) / ray_direction_x
        wall_x = player_y + distance * ray_direction_y
    else:
        distance = (map_y - player_y + (1 - step_y) / 2) / ray_direction_y
        wall_x = player_x + distance * ray_direction_x

    wall_x -= math.floor(wall_x)
    return max(distance, 0.001), wall_x, side, level.definition_at(map_x, map_y)


def cached_wall_strip(cache, texture_name, texture, texture_x, height, darkness):
    shade = min(240, darkness // 16 * 16)
    key = (texture_name, texture_x, height, shade)
    strip = cache.get(key)
    if strip is None:
        source = texture.subsurface((texture_x, 0, 1, texture.get_height()))
        strip = pygame.transform.scale(source, (1, height)).copy()
        strip.fill((255 - shade,) * 3, special_flags=pygame.BLEND_RGB_MULT)
        cache[key] = strip
    return strip


def render_world(surface, level, position, direction, walls, wall_cache):
    width, height = surface.get_size()
    surface.fill((22, 18, 24))
    pygame.draw.rect(surface, (38, 25, 24), (0, height // 2, width, height // 2))

    direction_x, direction_y = math.cos(direction), math.sin(direction)
    plane_scale = math.tan(FOV / 2)
    plane_x, plane_y = -direction_y * plane_scale, direction_x * plane_scale
    depth_buffer = [MAX_VIEW_DISTANCE] * width

    for column in range(width):
        camera_x = 2 * column / width - 1
        ray_x = direction_x + plane_x * camera_x
        ray_y = direction_y + plane_y * camera_x
        distance, wall_x, side, definition = cast_ray(
            level, position[0], position[1], ray_x, ray_y
        )
        depth_buffer[column] = distance
        line_height = int(height / distance)
        draw_start = max(0, height // 2 - line_height // 2)
        draw_end = min(height, height // 2 + line_height // 2)

        texture_name = definition.name if definition else "border"
        texture = walls.get(texture_name, walls["border"])
        texture_x = min(texture.get_width() - 1, int(wall_x * texture.get_width()))
        darkness = min(220, int(distance * 15) + (22 if side else 0))
        strip = cached_wall_strip(
            wall_cache,
            texture_name,
            texture,
            texture_x,
            max(1, draw_end - draw_start),
            darkness,
        )
        surface.blit(strip, (column, draw_start))

    return depth_buffer, (direction_x, direction_y, plane_x, plane_y)


def render_sprites(surface, level, position, camera, depth_buffer, sprite_images, sprite_cache):
    width, height = surface.get_size()
    direction_x, direction_y, plane_x, plane_y = camera
    determinant = plane_x * direction_y - direction_x * plane_y
    if determinant == 0:
        return
    inverse = 1.0 / determinant

    visible = [obj for obj in level.objects if obj.active and obj.definition.object_type != "door"]
    visible.sort(key=lambda obj: (obj.x - position[0]) ** 2 + (obj.y - position[1]) ** 2, reverse=True)

    for obj in visible:
        relative_x = obj.x - position[0]
        relative_y = obj.y - position[1]
        transform_x = inverse * (direction_y * relative_x - direction_x * relative_y)
        transform_y = inverse * (-plane_y * relative_x + plane_x * relative_y)
        if transform_y <= 0.05:
            continue

        screen_x = int((width / 2) * (1 + transform_x / transform_y))
        sprite_size = min(height * 2, abs(int(height / transform_y)))
        if sprite_size < 2:
            continue
        draw_left = screen_x - sprite_size // 2
        draw_top = height // 2 - sprite_size // 2
        image = sprite_images.get(obj.definition.name)
        if image is None:
            continue
        darkness = min(205, int(transform_y * 15))
        shade = darkness // 16 * 16
        cache_key = (obj.definition.name, sprite_size, shade)
        scaled = sprite_cache.get(cache_key)
        if scaled is None:
            scaled = pygame.transform.scale(image, (sprite_size, sprite_size)).copy()
            scaled.fill((255 - shade,) * 3, special_flags=pygame.BLEND_RGB_MULT)
            sprite_cache[cache_key] = scaled

        sample_left = max(0, min(width - 1, draw_left))
        sample_center = max(0, min(width - 1, screen_x))
        sample_right = max(0, min(width - 1, draw_left + sprite_size - 1))
        if transform_y < max(
            depth_buffer[sample_left],
            depth_buffer[sample_center],
            depth_buffer[sample_right],
        ):
            surface.blit(scaled, (draw_left, draw_top))


def process_objects(level, position):
    for obj in level.objects:
        if not obj.active:
            continue
        distance = math.hypot(obj.x - position[0], obj.y - position[1])
        if obj.definition.object_type == "gem" and distance < 0.45:
            obj.active = False
        elif obj.definition.object_type == "enemy" and obj.definition.kills_player and distance < 0.38:
            return "dead"
        elif obj.definition.object_type == "door" and door_is_open(level) and distance < 0.5:
            return "won"
    return None


def draw_hud(screen, level, font, fps, render_size):
    gems = sum(obj.active and obj.definition.object_type == "gem" for obj in level.objects)
    message = (
        f"Gems: {gems}   {fps:.0f} FPS   Render: {render_size[0]}x{render_size[1]}   "
        "WASD move   Mouse/Arrows turn   F11 fullscreen   -/+ quality   Esc quit"
    )
    screen.blit(font.render(message, True, (245, 225, 185)), (12, 10))


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Tuer le canard")
    render_quality = DEFAULT_RENDER_QUALITY
    render_surface = pygame.Surface(RENDER_SIZES[render_quality]).convert()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 26)
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    pygame.mouse.get_rel()

    level = load_level(
        SOURCE_PROJECT / "maps/game/map1.csv",
        SOURCE_PROJECT / "rules/objects.csv",
    )
    walls, sprites = load_assets()
    position = [level.spawn[0], level.spawn[1]]
    direction = math.pi
    status = None
    fullscreen = False
    wall_cache = {}
    sprite_cache = {}

    while status is None:
        delta_seconds = min(clock.tick(60) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                status = "quit"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                fullscreen = not fullscreen
                flags = pygame.FULLSCREEN if fullscreen else 0
                screen = pygame.display.set_mode(SCREEN_SIZE, flags)
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                render_quality = max(0, render_quality - 1)
                render_surface = pygame.Surface(RENDER_SIZES[render_quality]).convert()
                wall_cache.clear()
                sprite_cache.clear()
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                render_quality = min(len(RENDER_SIZES) - 1, render_quality + 1)
                render_surface = pygame.Surface(RENDER_SIZES[render_quality]).convert()
                wall_cache.clear()
                sprite_cache.clear()

        keys = pygame.key.get_pressed()
        mouse_delta_x, _mouse_delta_y = pygame.mouse.get_rel()
        direction += mouse_delta_x * MOUSE_SENSITIVITY
        direction += (float(keys[pygame.K_RIGHT]) - float(keys[pygame.K_LEFT])) * TURN_SPEED * delta_seconds
        move_player(level, position, direction, delta_seconds, keys)
        update_enemies(level, delta_seconds)
        status = process_objects(level, position)

        depth_buffer, camera = render_world(
            render_surface, level, position, direction, walls, wall_cache
        )
        render_sprites(
            render_surface,
            level,
            position,
            camera,
            depth_buffer,
            sprites,
            sprite_cache,
        )
        screen.blit(pygame.transform.scale(render_surface, screen.get_size()), (0, 0))
        draw_hud(screen, level, font, clock.get_fps(), render_surface.get_size())
        pygame.display.flip()

    pygame.quit()
    print(status.upper())


if __name__ == "__main__":
    main()
