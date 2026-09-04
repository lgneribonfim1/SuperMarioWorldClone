import pygame
from src.game.resources.effects.effect_assets import effects_assets
from src.game.world.effects.sparkle_particle import SparkleParticle


class CoinSpawn(pygame.sprite.Sprite):
    def __init__(self, pos, coin_frames, game, level):
        super().__init__()
        self.frames = coin_frames
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.frames[0]

        # Começa exatamente na posição da caixa
        self.rect = self.image.get_rect(topleft=pos)
        self.start_y = pos[1]

        self.game = game
        self.level = level

        # Velocidade inicial de subida
        self.vel_y = -6
        self.finished = False

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))

    def update(self):
        if self.finished:
            return

        # 1. Animação de Subida e Desaceleração
        self.rect.y += self.vel_y
        self.vel_y += 0.3  # Desacelera suavemente até parar

        # 2. Animação de Giro
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

        # 3. Quando atingir o topo (subiu cerca de 60 pixels)
        if self.rect.y <= self.start_y - 60:
            self.finish()

    def finish(self):
        self.finished = True

        # --- A MÁGICA DO SPARKLE (Reaproveitando o seu código) ---
        # Adiciona as partículas de brilho exatamente como no seu coin.py
        self.level.effects.add(
            SparkleParticle(self.rect.center, effects_assets.get_sparkle(), offset=(0, -8), delay=0),
            SparkleParticle(self.rect.center, effects_assets.get_sparkle(), offset=(8, 0), delay=3),
            SparkleParticle(self.rect.center, effects_assets.get_sparkle(), offset=(0, 8), delay=6),
            SparkleParticle(self.rect.center, effects_assets.get_sparkle(), offset=(-8, 0), delay=9)
        )

        # Adiciona as 10 moedas ao jogador e atualiza o HUD
        # self.game.coins += 10
        # if hasattr(self.level, 'hud'):
            # self.level.hud.update()

        # Remove a moeda da tela
        self.level.game.audio.play_sound("coin")
        player = self.level.player.sprite
        player.add_coin()
        self.kill()