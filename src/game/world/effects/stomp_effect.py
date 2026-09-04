import pygame
from src.game.world.effects.effect import Effect


class StompEffect(Effect):
    def __init__(self, pos, image, duration=12):
        super().__init__(pos)
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.duration = duration
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer >= self.duration:
            self.kill()