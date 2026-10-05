# /// script
# dependencies = ["pygame-ce"]
# ///
"""Pygbag entry point. Existing modules supply menus and both game modes."""
import asyncio
import pygame

from runtime.main_menu import main_menu

asyncio.run(main_menu())
