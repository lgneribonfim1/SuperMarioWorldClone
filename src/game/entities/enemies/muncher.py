import pygame
from src.game.entities.enemy import Enemy


class Muncher(Enemy):
    """Planta preta que abre e fecha como uma tesoura. Fica parada no chão,
    anima os dois frames, e causa dano se o jogador encostar nela. O único
    jeito de passar por cima ileso é com o pulo girando (spin jump), que
    faz o jogador quicar para cima."""

    def __init__(self, pos, frames, game):
        super().__init__(pos, frames)
        self.game = game

        # Animação simples: alterna entre aberta e fechada
        self.animation_speed = 0.1  # troca de frame a cada ~10 frames
        self.hitbox = self.rect.inflate(-6, -6)
        self.image = self.frames[0]  # começa aberta

    def update(self, player, prev_player_rect=None, prev_player_hitbox=None):
        if not self.alive:
            return

        # Anima a boca (abre/fecha)
        self.animate()

        # Atualiza a hitbox (mesmo parado, garante alinhamento)
        self.hitbox.center = self.rect.center

        # ============================================================
        # COLISÃO COM O PLAYER
        # ============================================================
        if self.hitbox.colliderect(player.hitbox):
            TOLERANCE = 16
            # Verifica se a colisão foi "por cima" (usando posição anterior)
            is_overlap_from_top = prev_player_rect.bottom <= self.rect.top + TOLERANCE

            if is_overlap_from_top:
                if player.spinning:
                    # Pulo girando: quica e não sofre dano
                    player.direction.y = -10
                    self.game.audio.play_sound('stomp_no_damage')
                    from src.game.world.effects.stomp_effect import StompEffect
                    from src.game.resources.effects.effect_assets import effects_assets
                    if hasattr(player, 'level') and player.level:
                        player.level.effects.add(StompEffect(
                            (self.rect.centerx, self.rect.top),
                            effects_assets.get_stomp()
                        ))
                else:
                    # Pisão sem giro: sofre dano
                    if player.big:
                        player.shrink()
                        player.direction.y = -4
                    else:
                        if hasattr(player, 'level') and player.level:
                            player.level.death_triggered = True
                            player.die()
            else:
                # Colisão lateral (ou por baixo): sempre sofre dano
                if player.invincible:
                    pass
                elif player.big:
                    player.shrink()
                else:
                    if hasattr(player, 'level') and player.level:
                        player.level.death_triggered = True
                        player.die()
        # ============================================================

    def draw(self, surface, camera):
        if self.alive:
            surface.blit(self.image, camera.apply(self.rect))