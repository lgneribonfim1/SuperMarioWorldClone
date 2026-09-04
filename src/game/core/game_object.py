import pygame


class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = None
        self.rect = None

    def update(self):
        pass

    def draw(self, surface, camera):
        if self.image and self.rect:
            surface.blit(self.image, camera.apply(self.rect))