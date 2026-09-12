import pygame
from src.game.entities.enemy import Enemy


class Chuck(Enemy):
    """
    Classe base compartilhada por todas as variantes do Chargin' Chuck.

    Mecânica central:
      - Vida: 3 pisões, 1 giro de capa, 4 fireballs.
      - Trigger por proximidade.
      - Reação a dano: knockback + 3 frames de hurt por nível de vida.

    Estados: "idle" -> "active" -> "hurt" -> "dead"
             (opcional: "look", para variantes como LookoutChuck)
    """

    MAX_HEALTH = 3
    TRIGGER_DISTANCE = 230

    def __init__(self, pos, frame_sets, game):
        super().__init__(pos, frame_sets["run"])
        self.game = game
        self.level = None

        # Frame sets
        self.run_frames = frame_sets.get("run", [])
        self.jump_frame = frame_sets.get("jump")
        self.look_frames = frame_sets.get("look", [])
        self.hurt_frames = frame_sets.get("hurt", [])
        self.pass_frames = frame_sets.get("pass", [])
        self.look_back_frames = frame_sets.get("look_back", [])
        self.search_frames = frame_sets.get("search", [])

        # Vida
        self.health = self.MAX_HEALTH
        self.hurt_timer = 0
        self.is_hurt = False
        self.hurt_frame_index = 0
        self.hurt_base_index = 0  # <-- ADICIONADO

        # Estado
        self.state = "idle"

        # Física
        self.velocity_y = 0
        self.gravity = 0.8
        self.on_ground = False

        # Direção
        self.direction.x = -1
        self.facing_right = False

        # Animação
        self.animation_speed = 0.15
        self.frame_index = 0

        # Hitbox
        self.hitbox = self.rect.inflate(-16, -16)

        # Timer de morte
        self.dead_timer = 0

    # =========================================================
    # MÉTODOS SOBRESCREVÍVEIS (variantes implementam)
    # =========================================================
    def on_activate(self, player):
        """Chamado UMA vez quando o player entra no raio de ativação."""
        pass

    def behavior(self, player):
        """Comportamento contínuo enquanto ativo."""
        pass

    def look_behavior(self, player):
        """Estado 'look': variantes podem sobrescrever (ex: LookoutChuck)."""
        pass

    def idle_behavior(self, player):
        """Comportamento enquanto idle (padrão: ficar parado olhando)."""
        if self.look_frames:
            self.image = self.look_frames[0]
            if self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

    def handle_player_collision(self, player, prev_player_rect):
        """Interação com o player. Padrão: stomp causa dano, contato fere."""
        is_stomp = (player.direction.y > 0 and
                    prev_player_rect is not None and
                    prev_player_rect.bottom <= self.rect.top + 16)

        if is_stomp:
            self.take_damage("stomp")
            player.direction.y = -12
            self.game.audio.play_sound("stomp_no_damage")
            self.game.audio.play_sound("stomp_koopa_kid")
        else:
            self._hurt_player(player)

    # =========================================================
    # SISTEMA DE VIDA (CORRIGIDO)
    # =========================================================
    def take_damage(self, damage_type="stomp"):
        """
        Aplica dano e MUDA o estado. O processamento dos estados
        ('hurt'/'dead') acontece no update().
        """
        if damage_type == "cape":
            self.health = 0
        else:
            self.health -= 1

        # --- Morreu ---
        if self.health <= 0:
            self.state = "dead"
            self.dead_timer = 15
            return True

        # --- Sobreviveu: entra em HURT ---
        self.state = "hurt"
        self.hurt_timer = 120
        self.hurt_duration = 120
        self.is_hurt = True

        # Frame-base do hurt conforme vida atual:
        # 3 vidas -> 0-2 | 2 vidas -> 3-5 | 1 vida -> 6-8
        self.hurt_base_index = (self.MAX_HEALTH - self.health - 1) * 3
        self.hurt_base_index = max(0, min(self.hurt_base_index, len(self.hurt_frames) - 3))
        self.hurt_frame_index = self.hurt_base_index
        return False

    def _hurt_player(self, player):
        if player.invincible:
            return
        elif player.big:
            player.shrink()
        else:
            if hasattr(player, 'level') and player.level:
                player.level.death_triggered = True
                player.die()

    # =========================================================
    # FÍSICA
    # =========================================================
    def apply_gravity(self, level):
        self.velocity_y += self.gravity
        self.rect.y += round(self.velocity_y)
        self.on_ground = False
        if level:
            for tile in level.collision_tiles:
                if tile.rect.colliderect(self.rect):
                    if self.velocity_y >= 0:
                        self.rect.bottom = tile.rect.top
                        self.velocity_y = 0
                        self.on_ground = True

    # =========================================================
    # UPDATE PRINCIPAL
    # =========================================================
    def update(self, player, prev_player_rect=None, prev_player_hitbox=None):
        if not self.alive:
            return

        level = player.level if hasattr(player, 'level') else None

        # --- Estado MORTO ---
        if self.state == "dead":
            # Congela no último frame de hurt (pose de derrota)
            if self.hurt_frames:
                self.image = self.hurt_frames[-1]
                if self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)

            # Pequeno delay antes de começar a cair (o "susto" do pisão)
            if self.dead_timer > 0:
                self.dead_timer -= 1
                self.hitbox.center = self.rect.center
                return

            # ==========================================================
            # QUEDA NO VAZIO (sem colisão com tiles — atravessa tudo)
            # ==========================================================
            self.velocity_y += self.gravity
            self.rect.y += round(self.velocity_y)
            self.hitbox.center = self.rect.center

            # Remove quando cai além do limite inferior do nível
            if level:
                death_threshold = level.world_origin.y + level.level_h + 200
            else:
                death_threshold = 2000

            if self.rect.top > death_threshold:
                self.kill()
            return

            # Anima os 3 últimos frames de hurt (6, 7, 8)
            if self.hurt_frames and len(self.hurt_frames) >= 9:
                frame_idx = 6 + ((60 - self.dead_timer) // 10) % 3
                frame_idx = min(frame_idx, len(self.hurt_frames) - 1)
                self.image = self.hurt_frames[frame_idx]
                if self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)

            if self.dead_timer <= 0:
                self.kill()
                return

            self.apply_gravity(level)
            self.hitbox.center = self.rect.center
            return

        # --- Estado HURT (animação avança pelos 3 frames) ---
        if self.state == "hurt":
            self.hurt_timer -= 1

            # Animação de hurt (mantém o frame correto)
            total = getattr(self, 'hurt_duration', 120)
            progress = 1.0 - (self.hurt_timer / total)
            frame_offset = min(int(progress * 3), 2)
            self.hurt_frame_index = self.hurt_base_index + frame_offset

            if self.hurt_frames:
                idx = min(self.hurt_frame_index, len(self.hurt_frames) - 1)
                self.image = self.hurt_frames[idx]
                if self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)

            if self.hurt_timer <= 0:
                self.is_hurt = False
                self.state = "idle"
                self.direction.x = -1
                self.facing_right = False

            self.apply_gravity(level)
            self.hitbox.center = self.rect.center

            # ==========================================================
            # COLISÃO DURANTE O HURT (comportamento especial)
            # ==========================================================
            self._handle_collision_during_hurt(player, prev_player_rect)
            return

        # --- Trigger por proximidade ---
        if self.state == "idle" and self._check_proximity(player):
            self.state = "active"
            self.on_activate(player)

        # --- Comportamento por estado ---
        if self.state == "active":
            self.behavior(player)
        elif self.state == "look":
            self.look_behavior(player)
        else:
            self.idle_behavior(player)

        # --- Física e hitbox ---
        self.apply_gravity(level)
        self.hitbox.center = self.rect.center

        # --- Colisão com o player ---
        if self.hitbox.colliderect(player.hitbox):
            if getattr(player, 'spinning', False):
                self.take_damage("cape")
            else:
                self.handle_player_collision(player, prev_player_rect)

    def _check_proximity(self, player):
        dx = abs(player.rect.centerx - self.rect.centerx)
        dy = abs(player.rect.centery - self.rect.centery)
        return dx < self.TRIGGER_DISTANCE and dy < 250

    def _handle_collision_during_hurt(self, player, prev_player_rect):
        """
        Colisão durante o estado 'hurt':
          - Pisão  -> player quica + efeito de stomp, Chuck NÃO leva dano.
          - Lateral -> player sofre dano (Chuck continua invulnerável).
          - Giro   -> Chuck morre (capa ainda funciona).
        """
        if not self.hitbox.colliderect(player.hitbox):
            return

        # Giro de capa mata instantaneamente, mesmo durante o hurt
        if getattr(player, 'spinning', False):
            self.take_damage("cape")
            return

        is_stomp = (player.direction.y > 0 and
                    prev_player_rect is not None and
                    prev_player_rect.bottom <= self.rect.top + 16)

        if is_stomp:
            # Player quica, Chuck NÃO leva dano
            player.direction.y = -12
            self.game.audio.play_sound("stomp_no_damage")

            # Efeito visual de stomp
            from src.game.world.effects.stomp_effect import StompEffect
            from src.game.resources.effects.effect_assets import effects_assets
            if hasattr(player, 'level') and player.level:
                player.level.effects.add(StompEffect(
                    (self.rect.centerx, self.rect.top),
                    effects_assets.get_stomp()
                ))
        else:
            # Colisão lateral: player sofre dano
            self._hurt_player(player)

    def draw(self, surface, camera):
        if self.alive:
            surface.blit(self.image, camera.apply(self.rect))