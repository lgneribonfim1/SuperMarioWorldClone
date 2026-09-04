import pygame
from src.game.entities.animated_entity import AnimatedEntity

class Enemy(AnimatedEntity):
    def __init__(self, pos, frames):
        super().__init__()
        self.frames = frames
        self.image = frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-4, -4)
        self.direction = pygame.math.Vector2()
        self.alive = True
        self.animation_speed = 0.15

    def animate(self):
        if len(self.frames) > 1:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[int(self.frame_index)]

    def kill(self):
        self.alive = False
        super().kill()
        # Aqui no futuro podemos adicionar um efeito de partícula (Sparkle)

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))