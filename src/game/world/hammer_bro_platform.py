import pygame
import math
from src.game.world.moving_platform import HorizontalPlatform


class HammerBroPlatform(HorizontalPlatform):
    """
    Plataforma específica para o Amazing Flying Hammer Brother.
    Herda de HorizontalPlatform e adiciona movimento vertical em arco
    (mais alto nas bordas, mais baixo no centro), lógica de transporte
    do AFHB e desenho das asas.
    """

    def __init__(self, pos, surface, speed=1.0, range=150, phase=0.0,
                 start_direction=1, vertical_amplitude=20):
        super().__init__(pos, surface, speed, range, phase, start_direction)
        self.afhb = None

        # Atributos para as asas
        self.wing_frames = []
        self.wing_frame_index = 0
        self.wing_animation_speed = 0.15

        # Parâmetros do movimento vertical em arco
        self.vertical_amplitude = vertical_amplitude  # Quantos pixels ela sobe/desce
        self.base_y = self.rect.y  # Guarda o Y inicial para calcular o arco

    def set_wing_frames(self, frames):
        self.wing_frames = frames

    def update(self, collision_tiles=None):
        # Executa o movimento horizontal original
        super().update(collision_tiles)

        # Calcula o progresso horizontal (0 a 1) do percurso
        if self.range != 0:
            progress = (self.rect.x - self.start_x) / self.range
        else:
            progress = 0

        # Aplica o movimento vertical parabólico:
        # Usamos uma "parábola invertida" para subir nas extremidades e descer no centro.
        # Fórmula: offset_y = amplitude * (1 - (2*progress - 1)^2)
        # - progress = 0 ou 1 (extremidades) -> offset = 0 (mais alto)
        # - progress = 0.5 (centro) -> offset = amplitude (mais baixo)
        offset_y = self.vertical_amplitude * (1 - (2 * progress - 1) ** 2)
        self.rect.y = self.base_y + offset_y

        # Transporta o AFHB (se existir e estiver vivo)
        if self.afhb is not None and self.afhb.alive:
            self.afhb.rect.centerx = self.rect.centerx
            self.afhb.rect.bottom = self.rect.top + 32
            self.afhb.hitbox.midtop = (self.afhb.rect.centerx, self.afhb.rect.top)

        # Animação das asas
        if self.wing_frames:
            self.wing_frame_index += self.wing_animation_speed
            if self.wing_frame_index >= len(self.wing_frames):
                self.wing_frame_index = 0

    def draw(self, surface, camera):
        # Desenha o bloco (base da plataforma)
        surface.blit(self.image, camera.apply(self.rect))

        # Desenha as asas (se existirem)
        if self.wing_frames:
            frame_index = int(self.wing_frame_index) % len(self.wing_frames)
            wing_image = self.wing_frames[frame_index]

            # Asa direita (colada na lateral direita do bloco)
            wing_right_rect = wing_image.get_rect(midleft=(self.rect.right, self.rect.centery))
            surface.blit(wing_image, camera.apply(wing_right_rect))

            # Asa esquerda (espelhada, colada na lateral esquerda)
            wing_left_image = pygame.transform.flip(wing_image, True, False)
            wing_left_rect = wing_left_image.get_rect(midright=(self.rect.left, self.rect.centery))
            surface.blit(wing_left_image, camera.apply(wing_left_rect))