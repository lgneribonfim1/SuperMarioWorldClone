import pygame
from src.game.world.moving_platform import HorizontalPlatform


class HammerBroPlatform(HorizontalPlatform):
    def __init__(self, pos, surface, speed=1.0, range=150, phase=0.0,
                 start_direction=1, vertical_amplitude=20):
        super().__init__(pos, surface, speed, range, phase, start_direction)
        self.afhb = None

        self.wing_frames = []
        self.wing_frame_index = 0
        self.wing_animation_speed = 0.15

        self.vertical_amplitude = vertical_amplitude
        self.base_y = self.rect.y

        # Controle do bump
        self.bump_velocity = 0
        self.bump_active = False

    def set_wing_frames(self, frames):
        self.wing_frames = frames

    def blocks_vertical_from_below(self):
        return True

    def bump(self, level):
        if self.bump_active:
            return
        level.game.audio.play_sound("bump")
        self.bump_active = True
        self.bump_velocity = -6

        if self.afhb is not None and self.afhb.alive:
            self.afhb.state = "dead"
            self.afhb.velocity_y = -8
            self.afhb.direction.y = 0

    def update(self, collision_tiles=None):
        # Guarda a posição Y ANTES de qualquer movimento
        prev_y = self.rect.y

        # 1. Movimento horizontal original (calcula delta_x)
        super().update(collision_tiles)

        # 2. Lógica do Bump (tem prioridade sobre o arco)
        if self.bump_active:
            self.rect.y += self.bump_velocity
            self.bump_velocity += 0.5
            if self.bump_velocity > 0:
                self.rect.y = self.base_y
                self.bump_active = False

        # 3. Movimento vertical em arco
        if not self.bump_active:
            if self.range != 0:
                progress = (self.rect.x - self.start_x) / self.range
            else:
                progress = 0
            offset_y = self.vertical_amplitude * (1 - (2 * progress - 1) ** 2)
            self.rect.y = self.base_y + offset_y

        # 4. Calcula o delta_y REAL (diferença entre o Y atual e o Y anterior)
        self.delta_y = self.rect.y - prev_y

        # 5. Transporta o AFHB (se existir e estiver vivo e não estiver morto)
        if self.afhb is not None and self.afhb.alive and self.afhb.state != "dead":
            self.afhb.rect.centerx = self.rect.centerx
            self.afhb.rect.bottom = self.rect.top + 32
            self.afhb.hitbox.midtop = (self.afhb.rect.centerx, self.afhb.rect.top)

        # 6. Animação das asas
        if self.wing_frames:
            self.wing_frame_index += self.wing_animation_speed
            if self.wing_frame_index >= len(self.wing_frames):
                self.wing_frame_index = 0

    def carry_player(self, player):
        """Move o jogador junto com a plataforma (horizontal E vertical)."""
        if player.current_ground_tile is self:
            # Move horizontal e verticalmente com base no delta real
            player.rect.x += self.delta_x
            player.rect.y += self.delta_y
            # Garante que o jogador esteja sempre alinhado ao topo
            player.rect.bottom = self.rect.top
            # Atualiza a hitbox e as variáveis auxiliares
            player.update_hitbox()
            player.float_x = player.rect.x
            player.float_y = player.rect.y

    def resolve_vertical_landing(self, player, prev_rect, previous_ground_tile):
        """Sobrescreve para lidar com o movimento vertical."""
        # Se já estava em cima, mantém o contato e realinha ao topo
        if previous_ground_tile is self:
            player.rect.bottom = self.rect.top
            player.direction.y = 0
            return self

        # Se está caindo e cruzou a plataforma, pousa e realinha
        if (player.direction.y >= 0 and
                prev_rect.bottom <= self.rect.top + 8 and
                player.rect.colliderect(self.rect)):
            player.rect.bottom = self.rect.top
            player.direction.y = 0
            player.on_ground = True
            player.current_ground_tile = self
            return self

        return None

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))

        if self.wing_frames:
            frame_index = int(self.wing_frame_index) % len(self.wing_frames)
            wing_image = self.wing_frames[frame_index]

            wing_right_rect = wing_image.get_rect(midleft=(self.rect.right, self.rect.centery - 16))
            surface.blit(wing_image, camera.apply(wing_right_rect))

            wing_left_image = pygame.transform.flip(wing_image, True, False)
            wing_left_rect = wing_left_image.get_rect(midright=(self.rect.left, self.rect.centery - 16))
            surface.blit(wing_left_image, camera.apply(wing_left_rect))