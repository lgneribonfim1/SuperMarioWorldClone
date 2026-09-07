import pygame
from src.game.entities.enemy import Enemy


class Hammer(Enemy):
    def __init__(self, pos, frames, direction, game):
        super().__init__(pos, frames)
        self.game = game
        self.direction.x = direction  # 1 para direita, -1 para esquerda
        self.velocity_y = -10  # Impulso inicial para cima
        self.gravity = 0.5
        self.animation_speed = 0.25

        self.hitbox = self.rect.inflate(-6, -6)

    def update(self, player=None, prev_player_rect=None, prev_player_hitbox=None):
        if not self.alive:
            return

        # Movimento em parábola
        self.rect.x += self.direction.x * 5
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # ==========================================
        # ANIMAÇÃO COM ITERAÇÃO REVERSA PARA A DIREITA
        # ==========================================
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        if self.direction.x > 0:  # Indo para a DIREITA
            self.image = pygame.transform.flip(self.frames[int(self.frame_index)], True, False)
        else:  # Indo para a ESQUERDA
            self.image = self.frames[int(self.frame_index)]

        # Atualiza a hitbox
        self.hitbox.center = self.rect.center

        # Destruição ao sair da tela ou bater no chão
        if self.rect.top > 600 or self.rect.left < -100 or self.rect.right > 900:
            self.kill()

    def draw(self, surface, camera):
        if self.alive:
            surface.blit(self.image, camera.apply(self.rect))