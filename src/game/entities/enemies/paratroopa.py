import pygame
from src.game.entities.enemies.koopa import Koopa


class Paratroopa(Koopa):
    """Koopa alado (Para-Troopa). Herda toda a máquina de estados do Koopa
    (shell_idle, shell_sliding, empty, pop_out, dead…) e acrescenta o
    estado inicial "flying" — uma oscilação vertical em torno de um ponto
    de ancoragem, enquanto avança horizontalmente como o Koopa normal.

    Ao ser pisado sem girar: perde as asas e cai diretamente no estado
    "walking" (igual a um Koopa vermelho comum). A partir daí, toda a
    lógica herdada entra em cena sem mudança alguma.

    Ao ser pisado GIRANDO: vai direto pro casco (shell_idle), mesmo com
    asas — idêntico ao Koopa normal.

    Parâmetros extras em relação ao Koopa:
      fly_frames     — lista de 2 Surfaces (as duas poses de bater asas)
      fly_turn_frame — Surface única (pose de virada)
      fly_amplitude  — quantos pixels oscila pra cima e pra baixo (padrão: 24)
      fly_speed_y    — velocidade da oscilação (padrão: 1.5 px/frame)
    """

    def __init__(self, pos, frame_sets, game,
                 turns_at_edges=True, speed=1.0,
                 kicks_shells=False, hurts_on_unshelled_touch=False):
        super().__init__(pos, frame_sets, game,
                         turns_at_edges=turns_at_edges, speed=speed,
                         kicks_shells=kicks_shells,
                         hurts_on_unshelled_touch=hurts_on_unshelled_touch)

        # Frames exclusivos do vôo (vindos do frame_set, com fallback seguro)
        self.fly_frames = frame_sets.get("fly") or self.walk_frames
        self.fly_turn_frame = frame_sets.get("fly_turn") or self.fly_frames[0]

        # Estado inicial é "flying", não "walking"
        self.state = "flying"

        # Oscilação vertical
        self.fly_anchor_y = float(self.rect.y)   # ponto central da oscilação
        self.fly_amplitude = 10                    # px acima/abaixo do âncora
        self.fly_phase = 0.0                       # fase atual (em radianos)
        self.fly_speed_y = 0.05                    # rad/frame (~3°/frame, ~30 frames por ciclo)
        self.is_turning = False                    # True durante o frame de virada

        # Paratroopa não usa gravidade enquanto voa — sobrescreve aplica_gravity
        # no update() só pra esse estado.
        self.velocity_y = 0

    # ------------------------------------------------------------
    # ANIMAÇÃO DO VÔO (sobrescreve animate() só pra "flying")
    # ------------------------------------------------------------
    def animate(self):
        if self.state != "flying":
            # Todos os outros estados usam a animação herdada do Koopa.
            super().animate()
            return

        if self.is_turning:
            self.image = self.fly_turn_frame
        else:
            # Alterna os 2 frames de bater asas pelo frame_index normal
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.fly_frames):
                self.frame_index = 0
            self.image = self.fly_frames[int(self.frame_index)]

        if self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    # ------------------------------------------------------------
    # MOVIMENTO DE VÔO (sobrescreve a parte de movimento no update)
    # ------------------------------------------------------------
    def _fly_move(self, level):
        """Avança horizontalmente e oscila verticalmente em torno do âncora."""
        import math

        # Horizontal — igual ao walking, com detecção de parede/borda
        prev_dir = self.direction.x
        self._check_wall_and_turn(level, self.base_speed)
        self._check_edge_and_turn(level)

        # Se virou de direção, mostra o frame de virada por 1 ciclo de animação
        if self.direction.x != prev_dir:
            self.is_turning = True
            self.frame_index = 0
        else:
            self.is_turning = False

        # Oscilação vertical pura (senoidal) — sem gravidade, sem colisão vertical
        self.fly_phase += self.fly_speed_y
        target_y = self.fly_anchor_y + math.sin(self.fly_phase) * self.fly_amplitude
        self.rect.y = round(target_y)

    # ------------------------------------------------------------
    # COLISÃO COM O PLAYER — só sobrescreve o estado "flying"
    # ------------------------------------------------------------
    def _handle_player_collision(self, player, prev_player_rect):
        if self.state != "flying":
            # Todos os outros estados (walking, shell_*, empty, …): comportamento
            # herdado do Koopa sem qualquer mudança.
            super()._handle_player_collision(player, prev_player_rect)
            return

        # --- estado "flying" ---
        if player.direction.y < 0:
            return

        is_stomp = (prev_player_rect is not None
                    and player.direction.y > 0
                    and prev_player_rect.bottom <= self.rect.top + 16)

        if is_stomp:
            if player.spinning:
                # Giro destrói direto -> casco parado (igual ao Koopa normal)
                self.state = "shell_idle"
                self.shell_idle_timer = self.shell_idle_duration
                self.direction.x = 0
                player.direction.y = -8
                self.game.audio.play_sound("stomp")
            else:
                # Pisão simples: perde as asas, vira Koopa normal (state = "walking")
                # O âncora vertical não importa mais, o Koopa vai ao chão pela
                # gravidade normal (apply_gravity herdado cuida disso).
                self.state = "walking"
                self.velocity_y = 0
                player.direction.y = -8
                self.game.audio.play_sound("stomp")
        else:
            self._hurt_player(player)

    # ------------------------------------------------------------
    # UPDATE PRINCIPAL — injeta o estado "flying" no início
    # ------------------------------------------------------------
    def update(self, player, prev_player_rect=None, prev_player_hitbox=None):
        if not self.alive:
            return

        level = player.level if hasattr(player, 'level') else None

        if self.state == "flying":
            self.animate()
            self._fly_move(level)
            self.hitbox.center = self.rect.center

            if self.hitbox.colliderect(player.hitbox):
                self._handle_player_collision(player, prev_player_rect)
            return

        # Para qualquer outro estado (walking, shell_*, empty, dead…):
        # delega 100% ao Koopa pai, que já trata tudo.
        super().update(player, prev_player_rect, prev_player_hitbox)