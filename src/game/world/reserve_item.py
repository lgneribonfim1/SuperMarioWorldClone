import pygame
from src.game.settings import GRAVITY

class ReserveItem(pygame.sprite.Sprite):
    """Item reserva caindo. NÃO colide com tiles, apenas com o player.
    Nasce na caixa do HUD (canto superior esquerdo) e cai lentamente."""

    def __init__(self, pos, image, game):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-4, -4)
        self.game = game

        # Física da queda
        self.velocity_y = 0        # Pequeno pulo inicial para "sair" da caixa
        self.gravity = GRAVITY * 0.05  # Gravidade reduzida (cai devagar)
        self.delay_timer = 30       # Janela de escape (0.5s) para não coletar instantaneamente

    def update(self, player):
        # Movimento vertical
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        self.hitbox.center = self.rect.center

        # Janela de escape
        if self.delay_timer > 0:
            self.delay_timer -= 1
            return

        # Coleta apenas se o player encostar
        if self.hitbox.colliderect(player.hitbox):
            self.collect(player)

        # Remove se sair da tela (caiu no vazio)
        if self.rect.top > 800:
            self.kill()

    def collect(self, player):
        self.kill()
        if not player.big:
            player.grow()
        else:
            player.reserve_item = "mushroom"  # Volta para a caixa
            player.game.audio.play_sound("power-up")

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))