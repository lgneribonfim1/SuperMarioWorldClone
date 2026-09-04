import pygame
from src.game.settings import TILE_SIZE

class Mushroom(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-4, -4)

        # Movimento
        self.direction = pygame.math.Vector2(1, 0)
        self.speed = 2
        self.gravity = 0.5
        self.on_ground = False

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def collect(self, level):
        level.game.audio.play_sound("power-up")
        player = level.player.sprite
        player.collect_mushroom()
        self.kill()

    def update(self, tiles, blocks, player, level):
        # Colisão Horizontal
        self.rect.x += self.direction.x * self.speed
        for sprite in list(tiles) + list(blocks):
            if sprite.rect.colliderect(self.rect):
                if self.direction.x > 0:
                    self.rect.right = sprite.rect.left
                elif self.direction.x < 0:
                    self.rect.left = sprite.rect.right
                self.direction.x *= -1

        # Colisão Vertical
        self.apply_gravity()
        self.on_ground = False
        for sprite in list(tiles) + list(blocks):
            if sprite.rect.colliderect(self.rect):
                if self.direction.y > 0:
                    self.rect.bottom = sprite.rect.top
                    self.direction.y = 0
                    self.on_ground = True
                elif self.direction.y < 0:
                    self.rect.top = sprite.rect.bottom
                    self.direction.y = 0

        # ==========================================================
        # A CORREÇÃO CRUCIAL: Atualizar o hitbox para onde o rect foi
        # ==========================================================
        self.hitbox.center = self.rect.center
        # ==========================================================

        # ==========================================
        # VERIFICA SE O PLAYER ENCOSTOU NO COGUMELO
        # ==========================================
        if self.hitbox.colliderect(player.hitbox):
            self.collect(level)
        # ==========================================

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))