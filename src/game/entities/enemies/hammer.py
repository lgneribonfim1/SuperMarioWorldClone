import pygame
import random  # <--- ADICIONE O IMPORT
from src.game.entities.enemy import Enemy


class Hammer(Enemy):
    def __init__(self, pos, frames, direction, game):
        super().__init__(pos, frames)
        self.game = game
        self.direction.x = direction  # 1 para direita, -1 para esquerda

        # ==========================================
        # VELOCIDADES ALEATÓRIAS (Distância variável)
        # ==========================================
        # Impulso inicial para cima (entre -8 e -12). Quanto mais negativo, mais alto.
        self.velocity_y = random.uniform(-10, -6)

        # Velocidade horizontal (entre 4 e 6). Quanto maior, mais longe vai.
        self.horizontal_speed = random.uniform(2.0, 5.0)
        # ==========================================

        self.gravity = 0.5
        self.animation_speed = 0.25

        self.hitbox = self.rect.inflate(-6, -6)

    def _hurt_player(self, player):
        if player.invincible:
            return
        elif player.big:
            player.shrink()
        else:
            if hasattr(player, 'level') and player.level:
                player.level.death_triggered = True
                player.die()

    def update(self, player=None, prev_player_rect=None, prev_player_hitbox=None):
        if not self.alive:
            return

        # Movimento em parábola (usando a velocidade horizontal aleatória)
        self.rect.x += self.direction.x * self.horizontal_speed
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

        if player is not None and self.hitbox.colliderect(player.hitbox):
            self._hurt_player(player)

        if player is not None and hasattr(player, 'level') and player.level:
            level = player.level
            left_bound = level.world_origin.x - 200
            right_bound = level.world_origin.x + level.level_w + 200
            bottom_bound = level.world_origin.y + level.level_h + 300

            if (self.rect.right < left_bound or
                    self.rect.left > right_bound or
                    self.rect.top > bottom_bound):
                self.kill()
        else:
            # Fallback (caso o player não esteja disponível)
            if self.rect.top > 2000:
                self.kill()

    def draw(self, surface, camera):
        if self.alive:
            surface.blit(self.image, camera.apply(self.rect))