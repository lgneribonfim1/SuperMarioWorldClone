import pygame
from src.game.entities.enemy import Enemy
from src.game.entities.enemies.unshelled_koopa import UnshelledKoopa


class Koopa(Enemy):
    """Koopa Troopa genérico — a mesma classe serve pra qualquer cor, já que
    a máquina de estados é idêntica; só os PARÂMETROS mudam (ver __init__).

    Estados: "walking" -> "shell_idle" -> "shell_sliding" (chutado) / "pop_out"
    (expelido) -> "empty" (casco vazio, ainda chutável) -> "walking" de
    novo (se a criatura recuperar o casco) -- ou "dead" a partir de
    "shell_sliding" (giro do player).
    """

    def __init__(self, pos, frame_sets, game,
                 turns_at_edges=True, speed=1.0,
                 kicks_shells=False, hurts_on_unshelled_touch=False):
        super().__init__(pos, frame_sets["walk"])
        self.game = game

        self.walk_frames = frame_sets["walk"]
        self.shell_idle_frame = frame_sets["shell_idle"]
        self.shell_slide_frames = frame_sets["shell_slide"]
        self.unshelled_frames = frame_sets["unshelled"]
        self.pop_out_frames = frame_sets.get("pop_out") or self.unshelled_frames
        self.squashed_frame = frame_sets.get("squashed")

        self.turns_at_edges = turns_at_edges
        self.base_speed = speed
        self.kicks_shells = kicks_shells
        self.hurts_on_unshelled_touch = hurts_on_unshelled_touch

        self.state = "walking"
        self.direction.x = -1
        self.facing_right = False

        self.has_creature = True
        self.linked_koopa = None
        self.pre_shell_direction = self.direction.x

        self.velocity_y = 0
        self.gravity = 0.8
        self.on_ground = False

        self.animation_timer = 0
        self.animation_frame_duration = 6  # A cada 6 pixels andados, troca o frame

        self.slide_speed = 6.0
        self.shell_idle_timer = 0
        self.shell_idle_duration = 5
        self.dead_timer = 0
        self.empty_delay = 0

        # Dados da animação pop_out (agora no UnshelledKoopa, mas mantidos
        # aqui para compatibilidade)
        self.pop_out_frame_duration = 12
        self.pop_out_elapsed = 0

        self.hitbox = self.rect.inflate(-6, -4)
        self.flipped_vertically = False
        self.kick_grace_timer = 0

    def spawn_unshelled(self, level):
        unshelled = UnshelledKoopa(
            (self.rect.centerx, self.rect.bottom),
            self.pop_out_frames,
            self.unshelled_frames,
            self.game,
            linked_shell=self,
            squashed_frame=self.squashed_frame,
            speed=self.base_speed * 1.0,
            turns_at_edges=self.turns_at_edges,
            dash_speed=10.0,
            dash_distance=40,
            original_direction=self.pre_shell_direction
        )
        level.enemies.add(unshelled)
        self.linked_koopa = unshelled
        self.state = "empty"
        self.has_creature = False
        self.image = self.shell_idle_frame

        # ==========================================================
        # EFEITO DE POEIRA NO MOMENTO DA EXPULSÃO
        # ==========================================================
        from src.game.world.effects.dust_effect import DustEffect
        level.effects.add(DustEffect(
            (self.rect.centerx, self.rect.bottom),
            level.assets.get_dust_frames(),
            offset=(0, -4),
            animation_speed=0.3
        ))

    def reclaim_shell(self):
        if self.state == "empty":
            self.state = "walking"
            self.has_creature = True
            self.direction.x = -1
            self.facing_right = False
            self.shell_idle_timer = 0
            # CORREÇÃO EXTRA: Voltar o tamanho do corpo
            old_bottom = self.rect.bottom
            self.rect.height = 64  # (ou o tamanho original do Koopa andando)
            self.rect.bottom = old_bottom
            self.hitbox = self.rect.inflate(-6, -4)

    def _resize_to_shell(self):
        if self.state in ("shell_idle", "empty"):
            old_bottom = self.rect.bottom
            self.rect.height = 32
            self.rect.bottom = old_bottom
            self.hitbox = self.rect.inflate(-6, -4)

    # ------------------------------------------------------------
    # FÍSICA
    # ------------------------------------------------------------
    def apply_gravity(self, level):
        self.velocity_y += self.gravity
        self.rect.y += round(self.velocity_y)
        self.on_ground = False
        if level:
            for tile in level.collision_tiles:
                if tile.rect.colliderect(self.rect):
                    if self.velocity_y > 0:
                        self.rect.bottom = tile.rect.top
                        self.velocity_y = 0
                        self.on_ground = True

    def kick_by_shell(self):
        """Chamado quando um casco deslizante atinge este Koopa.
        Ele é arremessado ~3 tiles para cima, vira de ponta cabeça
        e cai no vazio (atravessando os tiles)."""
        if self.state == "dead_thrown":
            return

        # Sempre usa o casco parado como visual
        self.image = self.shell_idle_frame

        # Ajusta o rect para o tamanho do casco (32x32), preservando o centro
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)
        self.hitbox = self.rect.inflate(-6, -4)

        self.state = "dead_thrown"
        self.velocity_y = -13   # ~3 tiles de altura
        self.flipped_vertically = True
        self.game.audio.play_sound("kick1")

    def _check_wall_and_turn(self, level, speed):
        self.rect.x += self.direction.x * speed
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

    # ------------------------------------------------------------
    # ANIMAÇÃO
    # ------------------------------------------------------------
    def animate(self):
        if self.state == "shell_idle" or self.state == "empty":
            self.image = self.shell_idle_frame
            return

        if self.state == "pop_out":
            idx = self.pop_out_elapsed // self.pop_out_frame_duration
            idx = min(idx, len(self.pop_out_frames) - 1)
            self.image = self.pop_out_frames[idx]
            if self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            return

        frames = {
            "walking": self.walk_frames,
            "shell_sliding": self.shell_slide_frames,
            "unshelled": self.unshelled_frames,
        }.get(self.state)

        if not frames:
            return

        if self.state == "walking":
            self.image = self.walk_frames[int(self.frame_index)]
            if self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            return

        if self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    # ------------------------------------------------------------
    # COLISÃO COM O PLAYER (Método único e centralizado)
    # ------------------------------------------------------------
    def _handle_player_collision(self, player, prev_player_rect):
        print(f"[KOOPA] _handle_player_collision - state={self.state}")
        # ==========================================
        # 2. Calcula is_stomp (com margem de +16)
        # ==========================================
        is_stomp = (prev_player_rect is not None and
                    player.direction.y > 0 and
                    prev_player_rect.bottom <= self.rect.top + 16)

        # ==========================================
        # 3. Lógica por estado
        # ==========================================
        if self.state == "walking":
            if is_stomp:
                self.state = "shell_idle"
                self.shell_idle_timer = self.shell_idle_duration
                self.direction.x = 0
                player.direction.y = -8
                self.game.audio.play_sound("stomp")
                # EFEITO DE STOMP
                from src.game.world.effects.stomp_effect import StompEffect
                from src.game.resources.effects.effect_assets import effects_assets
                if hasattr(player, 'level') and player.level:
                    player.level.effects.add(StompEffect(
                        (self.rect.centerx, self.rect.centery),
                        effects_assets.get_stomp()
                    ))
            else:
                self._hurt_player(player)

        elif self.state == "shell_idle":
            # ==========================================
            # VERIFICAÇÃO DE STOMP ROBUSTA PARA O CASCO
            # ==========================================
            stomp_on_shell = (prev_player_rect is not None and
                              player.direction.y > 0 and
                              prev_player_rect.bottom <= self.rect.top + 20)
            if stomp_on_shell:
                # PISÃO NO CASCO PARADO -> chuta (shell_sliding)
                self.direction.x = 1 if player.rect.centerx < self.rect.centerx else -1
                self.state = "shell_sliding"
                self.game.audio.play_sound("bump")
                player.direction.y = -8
                # EFEITO DE STOMP
                from src.game.world.effects.stomp_effect import StompEffect
                from src.game.resources.effects.effect_assets import effects_assets
                if hasattr(player, 'level') and player.level:
                    player.level.effects.add(StompEffect(
                        (self.rect.centerx, self.rect.top),
                        effects_assets.get_stomp()
                    ))
            else:
                pass

        elif self.state == "shell_sliding":
            # Período de graça: recém-chutado não machuca o player
            if self.kick_grace_timer > 0:
                return
            if player.spinning:
                self.state = "dead"
                self.dead_timer = 60
                self.game.audio.play_sound("stomp_no_damage")
            elif is_stomp:
                self.state = "shell_idle"
                self.shell_idle_timer = self.shell_idle_duration
                self.direction.x = 0
                player.direction.y = -8
                self.game.audio.play_sound("stomp_no_damage")
                # EFEITO DE STOMP
                from src.game.world.effects.stomp_effect import StompEffect
                from src.game.resources.effects.effect_assets import effects_assets
                if hasattr(player, 'level') and player.level:
                    player.level.effects.add(StompEffect(
                        (self.rect.centerx, self.rect.top),
                        effects_assets.get_stomp()
                    ))
            else:
                self._hurt_player(player)

        elif self.state == "empty":
            if is_stomp:
                self.direction.x = 1 if player.rect.centerx < self.rect.centerx else -1
                self.state = "shell_sliding"
                self.kick_grace_timer = 15  # <-- 0,25s de graça
                self.game.audio.play_sound("bump")
                player.direction.y = -8
            else:
                # CHUTE LATERAL
                if player.direction.x != 0:
                    self.direction.x = 1 if player.direction.x > 0 else -1
                    self.state = "shell_sliding"
                    self.kick_grace_timer = 15  # <-- 0,25s de graça
                    self.game.audio.play_sound("bump")
                    # Afasta o casco do player para evitar sobreposição
                    self.rect.x += self.direction.x * 4
                    self.hitbox.center = self.rect.center
                else:
                    pass

        elif self.state == "unshelled":
            if self.hurts_on_unshelled_touch:
                self._hurt_player(player)
            else:
                self.state = "dead"
                self.dead_timer = 60
                self.game.audio.play_sound("stomp")

        elif self.state == "pop_out":
            if is_stomp:
                player.direction.y = -6

    def _hurt_player(self, player):
        if player.invincible:
            return
        elif player.big:
            player.shrink()
        else:
            if hasattr(player, 'level') and player.level:
                player.level.death_triggered = True
                player.die()

    # ------------------------------------------------------------
    # UPDATE PRINCIPAL
    # ------------------------------------------------------------
    def update(self, player, prev_player_rect=None, prev_player_hitbox=None):
        if not self.alive:
            return

        level = player.level if hasattr(player, 'level') else None

        # ==========================================================
        # ESTADO "DEAD_THROWN" — cai no vazio, virado de ponta cabeça
        # Verificado ANTES de qualquer outra coisa (incluindo animate)
        # ==========================================================
        if self.state == "dead_thrown":
            self.velocity_y += self.gravity
            self.rect.y += round(self.velocity_y)
            self.hitbox.center = self.rect.center

            if level:
                death_threshold = level.world_origin.y + level.level_h + 200
            else:
                death_threshold = 2000

            if self.rect.top > death_threshold:
                self.kill()
            return

        # --- Estado "dead" (Koopa pisado de forma normal) ---
        if self.state == "dead":
            self.dead_timer -= 1
            if self.dead_timer <= 0:
                self.kill()
            return

        self.animate()

        if self.kick_grace_timer > 0:
            self.kick_grace_timer -= 1

        # Movimento por estado
        if self.state == "walking":
            self._check_wall_and_turn(level, self.base_speed)
            self._check_edge_and_turn(level)
            # Sincroniza a animação com a distância percorrida
            self.animation_timer += abs(self.base_speed)
            if self.animation_timer >= self.animation_frame_duration:
                self.animation_timer -= self.animation_frame_duration
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames)

        elif self.state == "shell_idle":
            self._resize_to_shell()
            self.shell_idle_timer -= 1
            if self.shell_idle_timer <= 0:
                self.spawn_unshelled(level)
                return

        elif self.state == "empty":
            self._resize_to_shell()
            # O casco vazio não se move, mas pode ser chutado pelo player.
            # A única interação é com o player (tratada no método de colisão).
            # A recuperação do casco pela criatura é feita pelo UnshelledKoopa.


        elif self.state == "shell_sliding":
            self._check_wall_and_turn(level, self.slide_speed)
            # Atualiza a hitbox IMEDIATAMENTE após mover, antes de colidir
            self.hitbox.center = self.rect.center
            if level:
                for enemy in level.enemies:
                    if enemy is not self and getattr(enemy, 'alive', False) \
                            and self.hitbox.colliderect(enemy.hitbox):
                        if hasattr(enemy, 'kick_by_shell'):
                            enemy.kick_by_shell()
                        else:
                            enemy.kill()

        elif self.state == "unshelled":
            self._check_wall_and_turn(level, self.base_speed * 1.5)
            self._check_edge_and_turn(level)
            self.unshelled_timer -= 1
            if self.unshelled_timer <= 0:
                self.state = "walking"

        self.apply_gravity(level)
        self.hitbox.center = self.rect.center

        # ==========================================
        # Colisão com o player (chamada única e limpa)
        # ==========================================
        if self.hitbox.colliderect(player.hitbox):
            self._handle_player_collision(player, prev_player_rect)

        # ==========================================
        # Recuperação do casco pela criatura (se o UnshelledKoopa encostar)
        # ==========================================
        if self.state == "empty" and self.linked_koopa is not None and getattr(self.linked_koopa, 'alive', False):
            if self.hitbox.colliderect(self.linked_koopa.hitbox):
                self.reclaim_shell()
                self.linked_koopa.kill()

    def draw(self, surface, camera):
        if self.alive:
            image = self.image
            if self.flipped_vertically:
                image = pygame.transform.flip(image, False, True)
                image_rect = image.get_rect(center=self.rect.center)
            else:
                image_rect = image.get_rect(midbottom=self.rect.midbottom)
            surface.blit(image, camera.apply(image_rect))