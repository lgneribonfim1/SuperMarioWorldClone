import pygame
from src.game.entities.enemy import Enemy
from src.game.settings import TILE_SIZE


class JumpingPiranha(Enemy):
    def __init__(self, pos, frames, game):
        super().__init__(pos, frames)
        self.game = game

        self.rise_frames = [frames[0], frames[1]]
        self.descend_frames = [frames[0], frames[2], frames[1], frames[3]]

        self.frame_index = 0
        self.animation_speed = 0.15
        self.descend_animation_speed = 0.3

        self.state = "idle"
        self.idle_timer = 60
        self.jump_height = 320
        self.start_y = self.rect.y  # topo do cano
        self.top_y = self.start_y - self.jump_height
        self.vel_y = 0
        self.gravity = 0.3
        self.descent_speed = 1.3

        self.hitbox = self.rect.inflate(-6, -6)
        self.image = self.rise_frames[0]

    def _animate_rise(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.rise_frames):
            self.frame_index = 0
        self.image = self.rise_frames[int(self.frame_index)]

    def _animate_descend(self):
        self.frame_index += self.descend_animation_speed
        if self.frame_index >= len(self.descend_frames):
            self.frame_index = 0
        self.image = self.descend_frames[int(self.frame_index)]

    # ==========================================
    # NOVO MÉTODO: Verifica se o player está sobre o cano
    # ==========================================
    def is_player_on_pipe(self, player):
        # Pés do jogador (usa o rect, pois é o que representa o corpo todo)
        player_feet = player.rect.bottom

        # O marcador "JumpingPiranha" é colocado UMA LINHA ABAIXO do topo
        # visual do cano (dentro dele) — confirmado com o diagnóstico:
        # vertical_diff ficava travado em exatamente -32 (= -TILE_SIZE) com
        # o player parado em cima do cano. Por isso o topo de verdade do
        # cano é self.start_y - TILE_SIZE, não self.start_y direto.
        pipe_top_y = self.start_y - TILE_SIZE
        vertical_diff = player_feet - pipe_top_y
        vertical_ok = abs(vertical_diff) <= 6

        # Largura do cano: a piranha está centralizada, e o cano tem 2 tiles
        # (64 pixels). O centro do jogador deve estar dentro dessa largura.
        pipe_center = self.rect.centerx
        half_pipe_width = 32  # Metade da largura do cano (2 tiles = 64px)
        horizontal_diff = player.hitbox.centerx - pipe_center
        horizontal_ok = abs(horizontal_diff) <= half_pipe_width

        rising_fast = player.direction.y < -1

        return vertical_ok and horizontal_ok and not rising_fast

    def update(self, player, prev_player_rect, prev_player_hitbox):
        if not self.alive:
            return

        prev_top = self.rect.top

        # Lógica do pulo
        if self.state == "idle":
            self.image = self.rise_frames[0]
            self.idle_timer -= 1

            # ==========================================
            # Se o player estiver sobre o cano, reseta o timer e não sobe
            # ==========================================
            if self.is_player_on_pipe(player):
                self.idle_timer = 60  # Reseta para garantir que não suba
            else:
                if self.idle_timer <= 0:
                    self.state = "rising_closed"
                    self.vel_y = -((2 * self.gravity * self.jump_height) ** 0.5)
                    self.idle_timer = 60
            # ==========================================

        elif self.state == "rising_closed":
            self._animate_rise()
            self.vel_y += self.gravity
            self.rect.y += self.vel_y
            if self.vel_y >= 0 or self.rect.y <= self.top_y:
                self.state = "descending_open"
                if self.rect.y < self.top_y:
                    self.rect.y = self.top_y
                self.vel_y = 0
                self.frame_index = 0

        elif self.state == "descending_open":
            self._animate_descend()
            self.rect.y += self.descent_speed
            if self.rect.y >= self.start_y:
                self.rect.y = self.start_y
                self.state = "idle"
                self.frame_index = 0

        self.hitbox.center = self.rect.center

        # Colisão com o player (mesma lógica anterior)
        if self.hitbox.colliderect(player.hitbox):
            TOLERANCE = 16
            is_overlap_from_top = prev_player_rect.bottom <= prev_top + TOLERANCE

            if is_overlap_from_top:
                if player.spinning:
                    player.direction.y = -10
                    self.game.audio.play_sound('stomp_no_damage')
                else:
                    if player.big:
                        player.shrink()
                        player.direction.y = -4
                    else:
                        if hasattr(player, 'level') and player.level:
                            player.level.death_triggered = True
                            player.die()
            else:
                if player.spinning:
                    if player.big:
                        player.shrink()
                    else:
                        if hasattr(player, 'level') and player.level:
                            player.level.death_triggered = True
                            player.die()
                else:
                    if hasattr(player, 'level') and player.level:
                        if player.invincible:
                            pass
                        elif player.big:
                            player.shrink()
                        else:
                            player.level.death_triggered = True
                            player.die()

    def draw(self, surface, camera):
        if self.alive:
            surface.blit(self.image, camera.apply(self.rect))