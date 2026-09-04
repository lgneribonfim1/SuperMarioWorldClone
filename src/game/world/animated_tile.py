import pygame


class AnimatedTile(pygame.sprite.Sprite):
    def __init__(self, pos, frames):
        super().__init__()

        self.frames = frames
        self.frame_index = 0
        self.animation_speed = 0.12

        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)

    def animate(self):
        if len(self.frames) == 1:
            self.image = self.frames[0]
            return

        self.frame_index += self.animation_speed

        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()

    def draw(self, surface, camera):
        surface.blit(self.image,camera.apply(self.rect))