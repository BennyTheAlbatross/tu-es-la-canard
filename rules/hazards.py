import pygame

from .sprits import TILE_SIZE


class CollapsingFloor:
    INTACT = 'intact'
    WOBBLE = 'wobble'
    CRACKED = 'cracked'
    COLLAPSED = 'collapsed'

    def __init__(self, x, y, images):
        self.rect = pygame.Rect(x, y, TILE_SIZE[0], TILE_SIZE[1])
        self.images = images
        self.state = self.INTACT
        self.state_elapsed = 0.0
        self.durations = {
            self.WOBBLE: 0.65,
            self.CRACKED: 0.45,
            self.COLLAPSED: 3.0,
        }

    @property
    def image(self):
        return self.images[self.state]

    @property
    def is_lethal(self):
        return self.state == self.COLLAPSED

    def trigger(self):
        if self.state == self.INTACT:
            self.state = self.WOBBLE
            self.state_elapsed = 0.0

    def update(self, delta_seconds):
        if self.state == self.INTACT:
            return

        self.state_elapsed += delta_seconds
        if self.state_elapsed < self.durations[self.state]:
            return

        self.state_elapsed = 0.0
        if self.state == self.WOBBLE:
            self.state = self.CRACKED
        elif self.state == self.CRACKED:
            self.state = self.COLLAPSED
        else:
            self.state = self.INTACT
