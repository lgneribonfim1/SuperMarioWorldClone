import pygame
from src.game.entities.enemy import Enemy


class UnshelledKoopa(Enemy):
    """Koopa sem casco, expelido e arremessado para longe do casco.
    - Imune a colisões durante a fase de pop_out.
    - Pisão por cima (após o pop_out): Koopa é esmagado e some.
    - Colisão lateral (após o pop_out): O jogador sofre dano.
    """

    def __init__(self, pos, pop_out_frames, unshelled_frames, game, linked_shell,
                 squashed_frame=None, speed=1.5, turns_at_edges=True, dash_speed=3.0,
                 dash_distance=40, original_direction=-1):  # <-- Adicionado novamente
        super().__init__(pos, pop_out_frames)
        self.game = game
        self.linked_shell = linked_shell
        self.pop_out_frames = pop_out_frames
        self.unshelled_frames = unshelled_frames
        self.squashed_frame = squashed_frame

        self.speed = speed
        self.turns_at_edges = turns_at_edges

        # ==========================================
        # Usa a direção original (antes do pisão)
        # ==========================================
        self.direction.x = original_direction if original_direction != 0 else -1
        self.facing_right = self.direction.x > 0
        # ==========================================

        # Deslocamento inicial
        self.rect.x += self.direction.x * dash_distance

        self.velocity_y = 0
        self.gravity = 0.8
        self.on_ground = False

        self.pop_out_phase = True
        self.pop_out_elapsed = 0
        self.pop_out_frame_duration = 12
        self.pop_out_total_duration = len(pop_out_frames) * self.pop_out_frame_duration

        self.dash_speed = dash_speed
        self.dash_friction = 0.4
        self.dash_until_speed = self.speed

        self.state = "walking"
        self.squash_timer = 0

        self.hitbox = self.rect.inflate(-8, -6)

    def apply_gravity(self, level):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        self.on_ground = False
        if level:
            for tile in level.collision_tiles:
                if tile.rect.colliderect(self.rect):
                    if self.velocity_y > 0:
                        self.rect.bottom = tile.rect.top
                        self.velocity_y = 0
                        self.on_ground = True

    def _check_wall_and_turn(self, level):
        current_speed = max(self.dash_speed, self.speed)
        self.rect.x += self.direction.x * current_speed
        if level:
            for tile in level.collision_tiles:
                if tile.rect.colliderect(self.rect):
                    if self.direction.x > 0:
                        self.rect.right = tile.rect.left
                    else:
                        self.rect.left = tile.rect.right
                    self.direction.x *= -1
                    self.facing_right = self.direction.x > 0
                    break

    def _check_edge_and_turn(self, level):
        if not self.turns_at_edges or not self.on_ground or not level:
            return
        foot_x = self.rect.centerx + self.direction.x * (self.rect.width // 2 + 4)
        foot_y = self.rect.bottom + 4
        has_ground_ahead = any(
            tile.rect.collidepoint(foot_x, foot_y) for tile in level.collision_tiles
        )
        if not has_ground_ahead:
            self.direction.x *= -1
            self.facing_right = self.direction.x > 0

    def _update_pop_out(self):
        idx = self.pop_out_elapsed // self.pop_out_frame_duration
        idx = min(idx, len(self.pop_out_frames) - 1)
        self.image = self.pop_out_frames[idx]
        if self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.dash_speed > self.dash_until_speed:
            self.dash_speed -= self.dash_friction
        else:
            self.dash_speed = self.speed

        self.pop_out_elapsed += 1
        if self.pop_out_elapsed >= self.pop_out_total_duration:
            self.pop_out_phase = False
            self.frames = self.unshelled_frames

    def _hurt_player(self, player):
        if player.invincible:
            return
        elif player.big:
            player.shrink()
        else:
            if hasattr(player, 'level') and player.level:
                player.level.death_triggered = True
                player.die()

    def animate(self):
        if not self.frames:
            return
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        if self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, player, prev_player_rect=None, prev_player_hitbox=None):
        if not self.alive:
            return

        level = player.level if hasattr(player, 'level') else None

        # Estado esmagado
        if self.state == "squashed":
            self.squash_timer -= 1
            if self.squash_timer <= 0:
                self.kill()
            return

        # Atualização da fase
        if self.pop_out_phase:
            self._update_pop_out()
        else:
            self.animate()

        # Movimento (mas NÃO vira durante o pop_out)
        if self.pop_out_phase:
            # Apenas se move reto, sem checar paredes ou bordas
            self.rect.x += self.direction.x * self.dash_speed
        else:
            self._check_wall_and_turn(level)
            self._check_edge_and_turn(level)

        self.apply_gravity(level)
        self.hitbox.center = self.rect.center

        # Colisão com o player (SOMENTE após o pop_out)
        if not self.pop_out_phase:
            if self.hitbox.colliderect(player.hitbox):
                if player.direction.y < 0:
                    pass
                else:
                    is_stomp = (prev_player_rect is not None and
                                player.direction.y > 0 and
                                prev_player_rect.bottom <= self.rect.top + 10)

                    if is_stomp:
                        if self.squashed_frame:
                            self.image = self.squashed_frame
                            self.state = "squashed"
                            self.squash_timer = 60
                        else:
                            self.kill()
                        player.direction.y = -8
                        self.game.audio.play_sound("stomp")
                    else:
                        self._hurt_player(player)

        # Recuperação do casco (também só após o pop_out)
        if not self.pop_out_phase:
            if self.linked_shell is not None and self.hitbox.colliderect(self.linked_shell.hitbox):
                self.linked_shell.reclaim_shell()
                self.kill()

    def draw(self, surface, camera):
        if self.alive:
            image_rect = self.image.get_rect(midbottom=self.rect.midbottom)
            surface.blit(self.image, camera.apply(image_rect))