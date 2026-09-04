from src.game.core.game_object import GameObject
from src.game.settings import GRAVITY
import pygame


class Entity(GameObject):
    def __init__(self):
        super().__init__()
        self.direction = pygame.math.Vector2()
        self.on_ground = False

    def apply_gravity(self):
        self.direction.y += GRAVITY