import pygame
from src.game.entities.enemies.chuck import Chuck


class LookoutChuck(Chuck):
    """
    Lookout Chuck (o clássico 'Chargin' Chuck').
    - Fica parado até o player se aproximar.
    - Corre na direção do player em alta velocidade.
    - Quando o player pula por cima, para, olha para trás em 3 fases
      e volta a perseguir.
    """

    def __init__(self, pos, frame_sets, game, charge_speed=4.5):
        super().__init__(pos, frame_sets, game)

        # ==========================================
        # ATRIBUTOS DE COMPORTAMENTO
        # ==========================================
        self.charge_speed = charge_speed

        # ==========================================
        # ATRIBUTOS DO ESTADO "LOOK"
        # ==========================================
        self.look_phase = "pass"           # "pass" -> "look_back" -> "search"
        self.look_frame_index = 0
        self.look_frame_timer = 0
        self.look_frame_duration = 7      # ticks por frame
        self.search_timer = 0
        self._last_debug_key = None

        self.look_cooldown = 0

        self.step = False

        # Som de passos
        self.last_played_frame = -1

    # =========================================================
    # ATIVAÇÃO
    # =========================================================
    def on_activate(self, player):
        self.direction.x = 1 if player.rect.centerx > self.rect.centerx else -1
        self.facing_right = self.direction.x > 0
        self.animation_speed = 0.25
        self.last_played_frame = -1

    # =========================================================
    # COMPORTAMENTO ATIVO (perseguição)
    # =========================================================
    def behavior(self, player):
        # ==========================================
        # DETECTA SE O PLAYER CRUZOU PARA O OUTRO LADO
        # ==========================================
        distance_x = player.rect.centerx - self.rect.centerx
        player_on_other_side = (
                (distance_x > 0 and self.direction.x < 0) or
                (distance_x < 0 and self.direction.x > 0)
        )
        player_is_close = abs(distance_x) < 250

        if (player_on_other_side and player_is_close and self.on_ground):
            self.state = "look"
            self.look_phase = "pass"
            self.look_frame_index = 0
            self.look_frame_timer = 0
            self.search_timer = 0
            self._last_debug_key = None
            return

        # ==========================================
        # MOVIMENTO DE PERSEGUIÇÃO
        # ==========================================
        self.rect.x += self.direction.x * self.charge_speed

        level = player.level if hasattr(player, 'level') else None
        if level:
            for tile in level.collision_tiles:
                if tile.rect.colliderect(self.rect):
                    if self.direction.x > 0:
                        self.rect.right = tile.rect.left
                    else:
                        self.rect.left = tile.rect.right

                    self.is_hurt = True
                    self.hurt_timer = 30
                    self.state = "hurt"
                    self.hurt_base_index = 0
                    self.hurt_frame_index = 0
                    self.velocity_y = -4
                    return

            if self.on_ground:
                foot_x = self.rect.centerx + self.direction.x * (self.rect.width // 2 + 4)
                foot_y = self.rect.bottom + 4
                has_ground = any(tile.rect.collidepoint(foot_x, foot_y)
                                 for tile in level.collision_tiles)
                if not has_ground:
                    self.direction.x *= -1
                    self.facing_right = self.direction.x > 0

        # ==========================================
        # ANIMAÇÃO DE CORRIDA + SOM DE PASSOS
        # ==========================================
        if self.run_frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.run_frames):
                self.frame_index = 0

            current_frame = int(self.frame_index)


            if current_frame != self.last_played_frame and self.on_ground:
                self.last_played_frame = current_frame
                if not self.step:
                    self.game.audio.play_sound("bump")
                    self.step = True
                else:
                    self.step = False

            self.image = self.run_frames[current_frame]
            if self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

    # =========================================================
    # COMPORTAMENTO DO ESTADO "LOOK"
    # =========================================================
    def look_behavior(self, player):
        """
        Fase 1 ('pass')      — Anda com os 3 frames da linha 4, em ordem
        Fase 2 ('look_back') — Anda com os 3 frames da linha 5, em ordem
        Fase 3 ('search')    — Para e procura o player (linha 6 em loop)
        """
        level = player.level if hasattr(player, 'level') else None

        # ==========================================
        # MOVIMENTO (só nas fases "pass" e "look_back")
        # ==========================================
        if self.look_phase in ("pass", "look_back"):
            self.rect.x += self.direction.x * self.charge_speed

            if level:
                for tile in level.collision_tiles:
                    if tile.rect.colliderect(self.rect):
                        if self.direction.x > 0:
                            self.rect.right = tile.rect.left
                        else:
                            self.rect.left = tile.rect.right
                        # Bateu na parede -> pula direto para "search"
                        self.look_phase = "search"
                        self.look_frame_index = 0
                        self.look_frame_timer = 0
                        self.search_timer = 0
                        self._last_debug_key = None
                        break

                if self.on_ground:
                    foot_x = self.rect.centerx + self.direction.x * (self.rect.width // 2 + 4)
                    foot_y = self.rect.bottom + 4
                    has_ground = any(tile.rect.collidepoint(foot_x, foot_y)
                                     for tile in level.collision_tiles)
                    if not has_ground:
                        self.direction.x *= -1
                        self.facing_right = self.direction.x > 0

        # ==========================================
        # ESCOLHE OS FRAMES DA FASE ATUAL
        # ==========================================
        if self.look_phase == "pass":
            frames = self.pass_frames
        elif self.look_phase == "look_back":
            frames = self.look_back_frames
        else:
            frames = self.search_frames

        if not frames:
            return

        # ==========================================
        # AVANÇA OS FRAMES (timer por frame, não total)
        # ==========================================
        self.look_frame_timer += 1
        if self.look_frame_timer >= self.look_frame_duration:
            self.look_frame_timer = 0
            self.look_frame_index += 1

            if self.look_phase in ("pass", "look_back") and self.on_ground:
                self.game.audio.play_sound("bump")

            if self.look_frame_index >= len(frames):
                # Fim da lista: transiciona de fase
                if self.look_phase == "pass":
                    self.look_phase = "look_back"
                elif self.look_phase == "look_back":
                    self.look_phase = "search"
                    self.search_timer = 0
                # "search" -> loop (não muda de fase)
                self.look_frame_index = 0
                self._last_debug_key = None

                # Re-fetch dos frames da nova fase
                if self.look_phase == "pass":
                    frames = self.pass_frames
                elif self.look_phase == "look_back":
                    frames = self.look_back_frames
                else:
                    frames = self.search_frames

        # ==========================================
        # DESENHA O FRAME ATUAL
        # ==========================================
        idx = min(self.look_frame_index, len(frames) - 1)
        self.image = frames[idx]
        if self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        # ==========================================
        # FIM DA FASE "search" (por tempo, pois é loop)
        # ==========================================
        if self.look_phase == "search":
            self.search_timer += 1
            if self.search_timer >= 90:
                self.look_cooldown = 60
                self.direction.x = 1 if player.rect.centerx > self.rect.centerx else -1
                self.facing_right = self.direction.x > 0
                self.state = "active"
                self.look_phase = "pass"
                self.look_frame_index = 0
                self.look_frame_timer = 0
                self._last_debug_key = None
                self.last_played_frame = -1

    # =========================================================
    # COLISÃO COM O PLAYER
    # =========================================================
    def handle_player_collision(self, player, prev_player_rect):
        super().handle_player_collision(player, prev_player_rect)