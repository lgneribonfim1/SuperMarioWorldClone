import pygame
from src.game.settings import *
from src.game.world.tile import SlopeTile


class PhysicsSystem:
    """Sistema de física e colisão para o player e entidades."""

    def __init__(self, world_origin):
        self.world_origin = world_origin

    def _get_nearby_tiles(self, player_rect, collision_tiles, blocks):
        """Pega apenas os tiles colisíveis que estão próximos ao jogador."""
        left_col = int((player_rect.left - self.world_origin.x) // TILE_SIZE) - 1
        right_col = int((player_rect.right - self.world_origin.x) // TILE_SIZE) + 1
        top_row = int((player_rect.top - self.world_origin.y) // TILE_SIZE) - 1
        bottom_row = int((player_rect.bottom - self.world_origin.y) // TILE_SIZE) + 1

        all_solids = list(collision_tiles) + list(blocks)
        nearby = []

        for solid in all_solids:
            solid_col = int((solid.rect.left - self.world_origin.x) // TILE_SIZE)
            solid_row = int((solid.rect.top - self.world_origin.y) // TILE_SIZE)

            if left_col <= solid_col <= right_col and top_row <= solid_row <= bottom_row:
                nearby.append(solid)

        return nearby

    def horizontal_collision(self, player, collision_tiles, blocks):
        """Resolve a colisão horizontal do player.
        platform_delta_x: deslocamento horizontal aplicado ao player pela plataforma.
        Se for diferente de 0, usamos ele para saber de qual lado expulsar o jogador.
        """
        # Movimento horizontal do player (se ele estiver andando)
        # Somamos o deslocamento da plataforma ao movimento do jogador
        player.rect.x += player.direction.x
        player.update_hitbox()

        nearby_solids = self._get_nearby_tiles(player.rect, collision_tiles, blocks)

        for solid in nearby_solids:
            if not solid.blocks_horizontal():
                continue

            if solid.rect.colliderect(player.rect):
                if player.direction.x > 0:
                    player.rect.right = solid.rect.left
                elif player.direction.x < 0:
                    player.rect.left = solid.rect.right

    def vertical_collision(self, player, prev_rect, collision_tiles, blocks, platforms=None):
        previous_ground_tile = player.current_ground_tile
        player.on_ground = False
        player.current_ground_tile = None

        # Aplica a gravidade ANTES de mover
        player.apply_gravity()
        player.rect.y += player.direction.y
        player.update_hitbox()

        # 1. Colisão com tiles comuns (blocos e terreno)
        nearby_solids = self._get_nearby_tiles(player.rect, collision_tiles, blocks)

        for solid in nearby_solids:
            if solid.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    landed_tile = solid.resolve_vertical_landing(player, prev_rect, previous_ground_tile)
                    if landed_tile is not None:
                        player.on_ground = True
                        player.current_ground_tile = landed_tile
                elif player.direction.y < 0:
                    if solid.blocks_vertical_from_below():
                        player.rect.top = solid.rect.bottom
                        player.direction.y = 0
                        if hasattr(solid, 'hit'):
                            solid.hit(player.level)

        # 2. Colisão com plataformas móveis (APENAS quando está caindo ou parado)
        if platforms:
            for platform in platforms:
                # Permitimos a colisão mesmo se direction.y < 0, desde que o jogador
                # já esteja sobre a plataforma no frame anterior (previous_ground_tile is platform)
                if (platform.rect.colliderect(player.rect) and
                        (player.direction.y >= 0 or player.current_ground_tile is platform)):
                    landed_tile = platform.resolve_vertical_landing(player, prev_rect, player.current_ground_tile)
                    if landed_tile is not None:
                        player.on_ground = True
                        player.current_ground_tile = landed_tile

        # 3. Ajuste de rampas (continua igual)
        if (player.on_ground and player.current_ground_tile
                and getattr(player.current_ground_tile, 'is_slope', False)
                and not getattr(previous_ground_tile, 'is_slope', False)):
            slope = player.current_ground_tile
            downhill = slope.downhill_direction()
            moving_uphill = (player.direction.x > 0 and downhill < 0) or \
                            (player.direction.x < 0 and downhill > 0)
            if moving_uphill:
                player.direction.x *= SLOPE_LANDING_DAMPING
                player.velocity_x = player.direction.x