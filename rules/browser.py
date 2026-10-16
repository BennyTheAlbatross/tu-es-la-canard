"""Small browser bridge; native keyboard and mouse continue through Pygame."""
import asyncio
import json
import sys

import pygame

IS_WEB = sys.platform == "emscripten"
_held = set()
_key_names = {
    "up": pygame.K_UP, "down": pygame.K_DOWN,
    "left": pygame.K_LEFT, "right": pygame.K_RIGHT,
    "enter": pygame.K_RETURN, "escape": pygame.K_ESCAPE,
    "torch": pygame.K_SPACE, "music": pygame.K_m, "walls": pygame.K_v,
}


async def next_frame(clock, fps=60):
    clock.tick(0 if IS_WEB else fps)
    await asyncio.sleep(0)


def is_touch_device():
    if not IS_WEB:
        return False
    import platform
    return bool(platform.window.navigator.maxTouchPoints) and bool(
        platform.window.matchMedia("(pointer:coarse)").matches
    )


def events():
    global _held
    result = pygame.event.get()
    if IS_WEB:
        import platform
        data = json.loads(str(platform.window.canardTakeInput()))
        _held = {_key_names[name] for name in data["held"] if name in _key_names}
        for name in data["actions"]:
            if name in _key_names:
                result.append(pygame.event.Event(pygame.KEYDOWN, key=_key_names[name]))
    return result


def keys():
    native = pygame.key.get_pressed()

    class Keys:
        def __getitem__(self, key):
            return key in _held or native[key]

    return Keys() if IS_WEB else native
