import pygame
from src.game.entities.enemy import Enemy
from src.game.entities.enemies.fireball import Fireball


class VolcanoLotus(Enemy):
    """Planta estacionária (nunca se move do lugar). Fica fechada por um
    tempo, abre em 4 estágios (fecha->abre1->abre2->totalmente aberta),
    dispara um leque simétrico de 4 bolas de fogo no estágio totalmente
    aberto, e fecha de novo — em ciclo. Comportamento e imunidades batem
    com o Super Mario World original: pulo normal machuca, giro só
    ricocheteia sem matar a planta nem se machucar (as bolas de fogo,
    porém, sempre machucam, giro ou não).
    """

    # Índices dos estágios de abertura (usados como frame_index em self.frames)
    CLOSED, OPEN_1, OPEN_2, FULL = 0, 1, 2, 3

    def __init__(self, pos, plant_frames, fireball_frames, game):
        # plant_frames deve ter exatamente 4 imagens, na ordem:
        # [fechada, abrindo 1, abrindo 2, totalmente aberta]
        super().__init__(pos, plant_frames)
        self.game = game
        self.fireball_frames = fireball_frames
        self.level = None  # setado de fora, igual ao Player (new_x.level = self)

        self.hitbox = self.rect.inflate(-8, -6)
        self.image = self.frames[self.CLOSED]

        # ------------------------------------------------------------
        # Máquina de estados da "respiração" (abre/fecha)
        # ------------------------------------------------------------
        self.stage = self.CLOSED
        self.opening = True  # True = indo em direção a FULL; False = voltando a CLOSED
        self.closed_timer = 150      # ~2.5s parada fechada antes de começar a abrir
        self.full_hold_timer = 20    # ~0.33s parada totalmente aberta (momento do disparo)
        self.frames_per_stage = 10   # frames de jogo gastos em cada transição de estágio
        self.stage_progress = 0
        self.has_fired_this_bloom = False

    def _advance_state_machine(self):
        if self.stage == self.CLOSED:
            self.closed_timer -= 1
            if self.closed_timer <= 0:
                self.opening = True
                self.stage = self.OPEN_1
                self.stage_progress = 0

        elif self.stage in (self.OPEN_1, self.OPEN_2):
            self.stage_progress += 1
            if self.stage_progress >= self.frames_per_stage:
                self.stage_progress = 0
                if self.opening:
                    self.stage = self.OPEN_2 if self.stage == self.OPEN_1 else self.FULL
                else:
                    self.stage = self.CLOSED if self.stage == self.OPEN_1 else self.OPEN_1
                    if self.stage == self.CLOSED:
                        self.closed_timer = 150

        elif self.stage == self.FULL:
            if not self.has_fired_this_bloom:
                self._spawn_fireballs()
                self.has_fired_this_bloom = True

            self.full_hold_timer -= 1
            if self.full_hold_timer <= 0:
                self.full_hold_timer = 20
                self.opening = False
                self.has_fired_this_bloom = False
                self.stage = self.OPEN_2
                self.stage_progress = 0

        self.image = self.frames[self.stage]

    def _spawn_fireballs(self):
        # Leque simétrico de 4 bolas de fogo, "abrindo" pros dois lados a
        # partir do topo da planta — mesmo espírito do leque de 4 do jogo
        # original. Ajuste os pares (vel_x, vel_y) para mudar o "espalhar".
        if self.level is None:
            return

        spawn_pos = (self.rect.centerx - 16, self.rect.top - 16)
        spread = [
            (-2.0, -2.2),
            (-0.5, -2.5),
            (0.5, -2.5),
            (2.0, -2.2),
        ]
        for vel_x, vel_y in spread:
            fireball = Fireball(spawn_pos, self.fireball_frames, self.game, vel_x, vel_y)
            self.level.fireballs.add(fireball)

    def update(self, player, prev_player_rect=None, prev_player_hitbox=None):
        if not self.alive:
            return

        self._advance_state_machine()
        self.hitbox.center = self.rect.center

        # ------------------------------------------------------------
        # Colisão com o corpo da planta (as bolas de fogo se cuidam
        # sozinhas em fireball.py). Sem distinção "por cima vs lateral"
        # aqui — no jogo original, tocar a planta de QUALQUER lado sem
        # estar girando machuca; girando, ricocheteia inofensivo.
        # ------------------------------------------------------------
        if self.hitbox.colliderect(player.hitbox):
            if player.spinning:
                player.direction.y = -8
                self.game.audio.play_sound('stomp_no_damage')
            else:
                if hasattr(player, 'level') and player.level:
                    if player.invincible:
                        pass
                    elif player.big:
                        player.shrink()
                        player.direction.y = -4
                    else:
                        player.level.death_triggered = True
                        player.die()

    def draw(self, surface, camera):
        if self.alive:
            surface.blit(self.image, camera.apply(self.rect))