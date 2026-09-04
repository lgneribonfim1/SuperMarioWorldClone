import pygame
from src.game.settings import *


class MovingPlatform(pygame.sprite.Sprite):
    """Classe base para plataformas móveis.
    Colisão apenas por cima (one-way).
    """

    def __init__(self, pos, surface, speed):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect
        self.speed = speed
        self.direction = pygame.math.Vector2(0, 0)
        self.delta_x = 0
        self.delta_y = 0

    def update(self):
        self.hitbox.topleft = self.rect.topleft

    def carry_player(self, player):
        """Move o jogador diretamente pelo deslocamento da plataforma."""
        if player.current_ground_tile is self:
            player.rect.x += self.delta_x
            player.rect.y += self.delta_y
            player.float_x = player.rect.x
            player.float_y = player.rect.y
            # Não alteramos player.direction.y aqui!
            # A física cuidará de zerá-la quando o pouso for confirmado.

    def resolve_vertical_landing(self, player, prev_rect, previous_ground_tile):
        """Verifica se o jogador pode pousar (one-way)."""
        # Se já estávamos em cima dela, mantemos o contato (mesmo subindo)
        if previous_ground_tile is self:
            return self

        # Se está caindo e estava acima, pousa normalmente
        if (player.direction.y >= 0 and
                prev_rect.bottom <= self.rect.top + 8 and
                player.rect.colliderect(self.rect)):
            player.rect.bottom = self.rect.top
            player.direction.y = 0
            player.on_ground = True
            player.current_ground_tile = self
            return self
        return None


class HorizontalPlatform(MovingPlatform):
    """Plataforma que se move horizontalmente, oscilando."""

    def __init__(self, pos, surface, speed=2, range=200, phase=0.0, start_direction=1):
        super().__init__(pos, surface, speed)
        self.range = range
        self.start_x = pos[0]
        self.initial_phase = max(0.0, min(1.0, phase))
        self.rect.x = self.start_x + (self.range * self.initial_phase)
        self.direction.x = 1 if start_direction >= 0 else -1

    def update(self, collision_tiles=None):
        prev_x = self.rect.x
        self.rect.x += self.direction.x * self.speed

        colidiu = False
        if collision_tiles:
            for tile in collision_tiles:
                if tile.rect.colliderect(self.rect):
                    self.rect.x = prev_x
                    self.direction.x *= -1
                    colidiu = True
                    break

        if not colidiu:
            if self.rect.x > self.start_x + self.range:
                self.rect.x = self.start_x + self.range
                self.direction.x *= -1
            elif self.rect.x < self.start_x:
                self.rect.x = self.start_x
                self.direction.x *= -1

        self.delta_x = self.rect.x - prev_x
        self.delta_y = 0
        super().update()

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))


class VerticalPlatform(MovingPlatform):
    """Plataforma que se move verticalmente, oscilando."""

    def __init__(self, pos, surface, speed=2, range=200, phase=0.0, start_direction=1):
        super().__init__(pos, surface, speed)
        self.range = range
        self.start_y = pos[1]
        self.initial_phase = max(0.0, min(1.0, phase))
        self.rect.y = self.start_y + (self.range * self.initial_phase)
        self.direction.y = 1 if start_direction >= 0 else -1

    def update(self, collision_tiles=None):
        prev_y = self.rect.y
        self.rect.y += self.direction.y * self.speed

        if self.rect.y > self.start_y + self.range:
            self.rect.y = self.start_y + self.range
            self.direction.y *= -1
        elif self.rect.y < self.start_y:
            self.rect.y = self.start_y
            self.direction.y *= -1

        self.delta_x = 0
        self.delta_y = self.rect.y - prev_y
        super().update()

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))