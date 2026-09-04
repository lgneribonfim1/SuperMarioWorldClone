import pygame


class Effect(pygame.sprite.Sprite):

    def __init__(self, pos):

        super().__init__()

        self.image = None
        self.rect = pygame.Rect(pos[0], pos[1], 0, 0)

    def update(self):
        pass

    def draw(self, surface, camera):

        surface.blit(
            self.image,
            camera.apply(self.rect)
        )