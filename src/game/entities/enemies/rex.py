import pygame
from src.game.entities.enemy import Enemy


class Rex(Enemy):
    def __init__(self, pos, big_frames, small_frames, dead_frame, game):
        super().__init__(pos, big_frames)
        self.big_frames = big_frames
        self.small_frames = small_frames
        self.dead_frame = dead_frame
        self.game = game

        self.size_state = "big"
        self.speed = 1
        self.direction.x = -1
        self.facing_right = False

        self.velocity_y = 0
        self.gravity = 0.8
        self.on_ground = False

        self.dead_timer = 0

        # Hitbox inicial (Rex grande tem altura de 64px)
        self.hitbox = self.rect.inflate(-8, -8)

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

    def update(self, player, prev_player_rect=None, prev_player_hitbox=None):
        if not self.alive:
            return

        if self.size_state == "dead":
            self.dead_timer -= 1
            if self.dead_timer <= 0:
                self.kill()
            return

        # ==========================================
        # Animação (conforme estado)
        # ==========================================
        if self.size_state == "big":
            self.animate(self.big_frames)
        else:
            self.animate(self.small_frames)
            self.speed = 1.5

        # Movimento horizontal
        self.rect.x += self.direction.x * self.speed

        if player.level:
            for tile in player.level.collision_tiles:
                if tile.rect.colliderect(self.rect):
                    if self.direction.x > 0:
                        self.rect.right = tile.rect.left
                    else:
                        self.rect.left = tile.rect.right
                    self.direction.x *= -1
                    self.facing_right = self.direction.x > 0
                    break

        # Gravidade
        self.apply_gravity(player.level if hasattr(player, 'level') else None)

        # Atualiza a hitbox
        self.hitbox.center = self.rect.center

        # ==========================================
        # Colisão com o player (Pisão)
        # ==========================================
        if self.hitbox.colliderect(player.hitbox):
            # Verificação robusta de "pisão": o jogador deve estar caindo E o fundo dele
            # deve estar acima do centro do Rex (com uma pequena margem).
            is_stomp = (player.direction.y > 0 and
                        player.rect.bottom < self.hitbox.centery + 10)

            if is_stomp:
                # ======================================
                # Lógica do pisão (grande → pequeno → morto)
                # ======================================
                if self.size_state == "big":
                    # 1. Encolhe para o estado pequeno
                    self.size_state = "small"
                    self.rect.height = 32
                    self.rect.bottom = self.rect.bottom
                    self.hitbox = self.rect.inflate(-6, -4)
                    self.game.audio.play_sound("stomp")
                    # QUIQUE MAIS FORTE (sai do alcance imediatamente)
                    player.direction.y = -10  # Antes era -8
                elif self.size_state == "small":
                    # 2. Rex pequeno é pisado -> morre
                    self.size_state = "dead"
                    self.image = self.dead_frame
                    self.dead_timer = 120  # 2 segundos
                    self.game.audio.play_sound("stomp")
                    player.direction.y = -8

            else:
                # ======================================
                # Colisão lateral (dano)
                # ======================================
                if player.invincible:
                    pass
                elif player.big:
                    player.shrink()
                else:
                    if hasattr(player, 'level') and player.level:
                        player.level.death_triggered = True
                        player.die()

    def animate(self, frames):
        if self.size_state == "big":
            self.frame_index += self.animation_speed * 0.5
        else:
            self.frame_index += self.animation_speed

        if self.frame_index >= len(frames):
            self.frame_index = 0
        self.image = frames[int(self.frame_index)]

        if self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def draw(self, surface, camera):
        if self.alive:
            # Ancora pelo CENTRO-INFERIOR (midbottom) de self.rect, em vez de
            # desenhar direto em cima de self.rect. Frames de tamanhos
            # ligeiramente diferentes (ex: o segundo frame do Rex pequeno,
            # 1px mais baixo que o primeiro) têm alturas de Surface
            # diferentes — desenhar sempre a partir do mesmo rect.y fixo faz
            # o frame mais baixo "flutuar" acima do chão pela diferença de
            # altura. Ancorando pelo pé (midbottom), cada frame é desenhado
            # exatamente onde o pé deveria tocar o chão, não importa sua
            # altura própria — mesmo princípio já usado em Player.draw().
            image_rect = self.image.get_rect(midbottom=self.rect.midbottom)
            surface.blit(self.image, camera.apply(image_rect))