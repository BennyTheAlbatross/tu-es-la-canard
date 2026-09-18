"""Small, failure-safe music controller shared by both game modes."""

from pathlib import Path

import pygame


PROJECT_DIR = Path(__file__).resolve().parent.parent
MUSIC_DIR = PROJECT_DIR / "assets" / "music"
DEFAULT_TRACK = MUSIC_DIR / "hellfeather_march.wav"
DEFAULT_VOLUME = 0.32

_enabled = True
_current_track = None


def _ensure_mixer():
    if pygame.mixer.get_init() is None:
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=1024)
        except pygame.error:
            return False
    return True


def play(track=DEFAULT_TRACK, volume=DEFAULT_VOLUME, restart=False):
    """Loop a music file. Audio failures never prevent the game from starting."""
    global _current_track
    path = str(Path(track))
    if not _enabled or not _ensure_mixer() or not Path(path).exists():
        return False
    if _current_track == path and pygame.mixer.music.get_busy() and not restart:
        return True
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        pygame.mixer.music.play(-1)
        _current_track = path
        return True
    except pygame.error:
        return False


def stop(fade_ms=350):
    if pygame.mixer.get_init():
        pygame.mixer.music.fadeout(max(0, fade_ms))


def toggle():
    """Toggle music globally and return the new enabled state."""
    global _enabled
    _enabled = not _enabled
    if _enabled:
        play()
    else:
        stop(150)
    return _enabled


def is_enabled():
    return _enabled
