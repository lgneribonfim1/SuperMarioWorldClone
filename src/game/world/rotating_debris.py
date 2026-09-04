import pygame
from src.game.world.animated_tile import AnimatedTile


class RotatingDebris(AnimatedTile):
    """Pedacinho que voa quando o bloco rotativo é destruído."""

    def __init__(self, center, frames, offset):
        # A imagem inicial é o primeiro frame (8x8 redimensionado para 16x16)
        super().__init__((0, 0), frames)
        self.rect.center = (center[0] + offset[0], center[1] + offset[1])
        self.hitbox = self.rect

        # Velocidade inicial (vai para cima e para os lados)
        self.velocity = pygame.math.Vector2(offset[0] / 8, -6)  # força para cima
        self.gravity = 0.5
        self.frame_index = 0

    def update(self):
        self.velocity.y += self.gravity
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Anima o destroço (opcional, pode usar um frame fixo ou girar)
        self.frame_index += 0.2
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

        # Remove se cair demais (ou após tempo)
        if self.rect.y > 600:
            self.kill()