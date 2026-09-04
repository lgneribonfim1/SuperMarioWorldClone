import pygame
from src.game.entities.enemy import Enemy


class Fireball(Enemy):
    """Bola de fogo disparada pela VolcanoLotus. Sobe, atinge um pico e
    desce devagar (gravidade reduzida em relação ao player) — igual ao
    comportamento clássico ("slowly rain down" depois de atingir o ponto
    mais alto). Sempre machuca o player no toque, mesmo girando (a única
    coisa que o giro neutraliza é o corpo da própria planta, não as bolas
    de fogo)."""

    def __init__(self, pos, frames, game, vel_x, vel_y):
        super().__init__(pos, frames)
        self.game = game
        self.velocity = pygame.math.Vector2(vel_x, vel_y)
        self.gravity = 0.03  # mais fraca que a do player (0.8) -> queda lenta, "chovendo"
        self.animation_speed = 0.3
        self.hitbox = self.rect.inflate(-6, -6)

        # Posição "de verdade" em ponto flutuante. self.rect.x/y são
        # inteiros — somar a velocidade DIRETO neles trunca a parte
        # fracionária a cada frame. Pra velocidades menores que 1px/frame
        # (como as duas bolas centrais do leque, vel_x=±0.5), isso fazia a
        # posição nunca sair do lugar (0.5 trunca pra 0 todo frame, pra
        # sempre) — era exatamente a causa da assimetria: as duas bolas
        # externas (vel_x=±2.0, sem parte fracionária) se moviam bem, e as
        # centrais ficavam praticamente paradas no eixo X.
        self.pos = pygame.math.Vector2(self.rect.topleft)

        # Despawn de segurança (a bola de fogo não colide com o cenário
        # nesta primeira versão — ver observação na conversa). Um timer
        # generoso cobre a subida + queda inteira sem deixá-la voando pra
        # sempre caso não encontre o player nem saia da tela.
        self.life_timer = 240  # ~4s a 60 FPS

    def update(self, player, prev_player_rect=None, prev_player_hitbox=None):
        # 1. Aplica a gravidade e move verticalmente
        self.velocity.y += self.gravity
        self.pos.y += self.velocity.y

        # ==========================================
        # 2. Movimento horizontal SIMÉTRICO
        # Aplica a gravidade PRIMEIRO e DEPOIS verifica se está subindo.
        # Isso garante que todas as bolas andem para o lado pelo EXATO
        # mesmo número de frames, eliminando a assimetria.
        # ==========================================
        if self.velocity.y < 0:
            # Ainda está subindo: anda para o lado
            self.pos.x += self.velocity.x
        else:
            # Atingiu o pico (ou está caindo): para de andar para o lado
            self.velocity.x = 0
        # ==========================================

        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.hitbox.center = self.rect.center
        self.animate()

        self.life_timer -= 1
        if self.life_timer <= 0:
            self.kill()
            return

        if self.hitbox.colliderect(player.hitbox):
            if hasattr(player, 'level') and player.level:
                if player.invincible:
                    pass
                elif player.big:
                    player.shrink()
                else:
                    player.level.death_triggered = True
                    player.die()
            self.kill()