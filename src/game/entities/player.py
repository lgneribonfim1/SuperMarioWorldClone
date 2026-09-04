import pygame
from src.game.settings import *
from src.game.entities.animated_entity import AnimatedEntity
from src.game.graphics.spritesheet import SpriteSheet
from src.game.resources.player_animations import PLAYER_ANIMATIONS


class Player(AnimatedEntity):
    def __init__(self, pos, character, game):
        super().__init__()
        self.game = game
        spritesheets = {
            "luigi": "assets/graphics/sprites/luigi_spritesheet.png",
            "mario": "assets/graphics/sprites/mario_spritesheet.png"
        }

        self.spritesheet = SpriteSheet(
            spritesheets[character],
            tile_width=48,
            tile_height=48,
            transparent_color=(255, 0, 255)
        )

        self.status = "idle"
        self.load_animations()
        self.image = self.animations[self.status][0]

        self.small_rect_size = (24, 42)
        self.big_rect_size = (24, 50)

        self.rect = pygame.Rect(pos[0], pos[1], *self.small_rect_size)
        self.hitbox = self.rect.inflate(-6, -2)
        self.facing_right = True

        self.big = False
        self.is_growing = False
        self.grow_timer = 0

        # ==========================================
        # ESTADO DE ENCOLHIMENTO
        # ==========================================
        self.is_shrinking = False
        self.shrink_timer = 0
        # ==========================================

        # ==========================================
        # ESTADO DE INVENCIBILIDADE (piscar após dano)
        # ==========================================
        self.invincible = False
        self.invincible_timer = 0
        # ==========================================

        # ==========================================
        # ESTADO DE MORTE
        # ==========================================
        self.is_dead = False
        # ==========================================

        # Estado do item reserva
        self.reserve_item = None
        self.c_pressed = False

        # Estado dos pulos
        self.spinning = False
        self.can_spin = True
        self.jump_pressed = False
        self.spin_pressed = False

        self.level = None
        self.current_ground_tile = None

        self.jump_time = 0
        self.max_jump_time = 12
        self.gravity = GRAVITY
        self.jump_gravity = GRAVITY * 0.35
        self.velocity_x = 0.0
        self.acceleration = 0.20
        self.deceleration = 0.25
        self.max_walk_speed = PLAYER_SPEED
        self.max_run_speed = PLAYER_SPEED * 1.8
        self.skidding = False

        self.score = 0
        self.coins = 0
        self.yoshi_coins = 0
        self.lives = START_LIVES

    def add_score(self, points):
        self.score += points

    def add_coin(self):
        self.coins += COIN
        self.add_score(COIN_POINTS)

    def add_yoshi_coin(self):
        """Adiciona 1 Yoshi Coin. Ao coletar 5, o jogador ganha 1 vida extra e o contador reseta."""
        self.yoshi_coins += 1

        # Usamos >= em vez de == para sermos robustos (se coletar 2 de uma vez, não quebra)
        if self.yoshi_coins >= 5:
            self.yoshi_coins -= 5  # Reseta (subtrai 5)
            self.lives += 1
            # self.game.audio.play_sound("dragon_coin")
            # (Opcional: você pode adicionar aqui um efeito visual de 1UP no HUD)


    def load_animations(self):
        self.animations = {}
        for animation_name, frame_list in PLAYER_ANIMATIONS.items():
            frames = []
            for row, col in frame_list:
                frame = self.spritesheet.extract_tile(row, col, scale=2)
                frames.append(frame)

            self.animations[animation_name] = frames

        # Frames reversos para o encolhimento (crescer ao contrário)
        self.shrink_frames = list(reversed(self.animations["growing"]))

    def start_invincibility(self, duration=120):
        """Ativa a invencibilidade (piscar) por um determinado tempo."""
        self.invincible = True
        self.invincible_timer = duration

    def die(self):
        if not self.is_dead:
            self.is_dead = True
            self.spinning = False
            self.is_shrinking = False
            self.invincible = False  # Cancela invencibilidade
            self.status = "death"
            self.animation_speed = 0
            self.direction.x = 0
            self.velocity_x = 0
            self.direction.y = 0
            self.game.audio.stop_music_instant()
            self.game.audio.play_sound("lost_a_life")

    def grow(self):
        if not self.big and not self.is_growing and not self.is_shrinking:
            self.is_growing = True
            self.status = "growing"
            self.grow_timer = 0
            self.animation_speed = 0.4
            self.rect.size = self.big_rect_size
            self.hitbox = self.rect.inflate(-6, -2)
            self.rect.midbottom = self.rect.midbottom

    def shrink(self):
        """Encolhe o player (se grande) com animação reversa e inicia invencibilidade."""
        if self.big and not self.is_shrinking:
            self.game.audio.play_sound("power_down_pipe")
            self.is_shrinking = True
            self.status = "growing"  # reutiliza a chave, frames serão reversos
            self.shrink_timer = 0
            self.frame_index = 0
            self.image = self.shrink_frames[0]
            self.drop_reserve_item()

    def collect_mushroom(self):
        if not self.big and not self.is_growing:
            self.grow()
        else:
            if self.reserve_item is None:
                self.reserve_item = "mushroom"
            else:
                self.add_coin()
                self.add_score(100)

    def drop_reserve_item(self):
        """Libera o item reserva para cair no mundo.
        O item nasce exatamente na posição da caixa de reserva no HUD (fixa na tela),
        convertida para coordenadas de mundo usando a câmera atual."""
        if self.reserve_item is not None and self.level is not None:
            from src.game.world.reserve_item import ReserveItem

            self.game.audio.play_sound("reserve_drop")

            # Posição da caixa no HUD (fixa na tela)
            box_x = 240
            box_y = 26

            # Converte para coordenadas de mundo usando a câmera atual
            world_x = int(self.level.camera.offset.x + box_x)
            world_y = int(self.level.camera.offset.y + box_y)

            item = ReserveItem(
                (world_x, world_y),
                self.level.assets.get_mushroom_image(),
                self.game
            )
            self.level.reserve_items.add(item)

            # Sempre esvazia a caixa (consumiu o item)
            self.reserve_item = None

    def get_input(self):
        # ==========================================
        # TRAVA DE MOVIMENTO QUANDO MORTO OU ENCOLHENDO
        # ==========================================
        if self.is_dead or self.is_shrinking:
            return
        # ==========================================

        keys = pygame.key.get_pressed()

        # RESETAR O ESTADO DE GIRO AO PISAR NO CHÃO
        if self.on_ground:
            self.spinning = False
            self.can_spin = True

        # ATRITO DE ACORDO COM O CHÃO
        on_slope = bool(self.on_ground and self.current_ground_tile
                         and getattr(self.current_ground_tile, 'is_slope', False))
        if on_slope:
            self.deceleration = 0.25 * self.current_ground_tile.friction_mod
        else:
            self.deceleration = 0.25

        # DEFINIÇÃO DA VELOCIDADE E ANIMAÇÃO
        if self.spinning:
            self.animation_speed = 0.35
            target_speed = self.max_walk_speed
        elif keys[pygame.K_LSHIFT]:
            target_speed = self.max_run_speed
            self.animation_speed = 0.28
        else:
            target_speed = self.max_walk_speed
            self.animation_speed = 0.16

        self.direction.x = 0

        # Movimento horizontal
        if keys[pygame.K_RIGHT]:
            self.velocity_x += self.acceleration
            if self.velocity_x > target_speed:
                self.velocity_x = target_speed
            self.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.velocity_x -= self.acceleration
            if self.velocity_x < -target_speed:
                self.velocity_x = -target_speed
            self.facing_right = False
        else:
            if self.velocity_x > 0:
                self.velocity_x -= self.deceleration
                if self.velocity_x < 0:
                    self.velocity_x = 0
            elif self.velocity_x < 0:
                self.velocity_x += self.deceleration
                if self.velocity_x > 0:
                    self.velocity_x = 0

        if self.velocity_x > 1 and keys[pygame.K_LEFT]:
            self.skidding = True
        elif self.velocity_x < -1 and keys[pygame.K_RIGHT]:
            self.skidding = True
        else:
            self.skidding = False

        self.direction.x = self.velocity_x

        # PULO NORMAL (ESPAÇO)
        if keys[pygame.K_SPACE]:
            if not self.jump_pressed and self.on_ground and not self.spinning:
                self.direction.y = JUMP_FORCE
                self.on_ground = False
                self.jump_time = 0
                self.spinning = False
                self.can_spin = True
                self.game.audio.play_sound("jump")
            self.jump_pressed = True
        else:
            self.jump_pressed = False

        # PULO GIRANDO (V)
        if keys[pygame.K_v]:
            if not self.spin_pressed and self.on_ground and not self.jump_pressed:
                self.spinning = True
                self.can_spin = False
                self.direction.y = JUMP_FORCE * 1.4
                self.on_ground = False
                self.jump_time = 0
                self.game.audio.play_sound("spin")
            self.spin_pressed = True
        else:
            self.spin_pressed = False

        # Liberar Item Reserva (Tecla C)
        if keys[pygame.K_c]:
            if not self.c_pressed and self.reserve_item is not None:
                self.drop_reserve_item()
            self.c_pressed = True
        else:
            self.c_pressed = False

    def apply_gravity(self):
        keys = pygame.key.get_pressed()
        if self.direction.y < 0 and keys[pygame.K_SPACE] and self.jump_time < self.max_jump_time:
            self.direction.y += self.jump_gravity
            self.jump_time += 1
        else:
            self.direction.y += self.gravity

    def get_status(self):
        # ==========================================
        # ESTADO DE MORTE (prioridade máxima)
        # ==========================================
        if self.is_dead:
            self.status = "death"
            return
        # ==========================================

        # ==========================================
        # ESTADO DE ENCOLHIMENTO (prioridade)
        # ==========================================
        if self.is_shrinking:
            self.status = "growing"
            return
        # ==========================================

        if self.is_growing:
            self.status = "growing"
            return

        if self.spinning:
            suffix = "_big" if self.big else ""
            self.status = f"spin_jump{suffix}"
            return

        if self.direction.y < 0:
            suffix = "_big" if self.big else ""
            self.status = f"jump{suffix}"
        elif self.direction.y > 1:
            suffix = "_big" if self.big else ""
            self.status = f"fall{suffix}"
        elif self.skidding:
            suffix = "_big" if self.big else ""
            self.status = f"skid{suffix}"
        elif abs(self.velocity_x) > 0.1:
            suffix = "_big" if self.big else ""
            if abs(self.velocity_x) > self.max_walk_speed:
                self.status = f"run{suffix}"
            else:
                self.status = f"walk{suffix}"
        else:
            suffix = "_big" if self.big else ""
            self.status = f"idle{suffix}"

    def animate(self):
        # Atualiza a invencibilidade (timer)
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        # ==========================================
        # ANIMAÇÃO DE ENCOLHIMENTO (frames reversos, mais lenta)
        # ==========================================
        if self.is_shrinking:
            self.shrink_timer += 1
            # A cada 4 frames, avança 1 frame da animação (velocidade mais lenta)
            if self.shrink_timer % 4 == 0:
                self.frame_index += 1

            if self.frame_index >= len(self.shrink_frames):
                # Termina o encolhimento
                self.is_shrinking = False
                self.big = False
                self.rect.size = self.small_rect_size
                self.hitbox = self.rect.inflate(-6, -2)
                self.rect.midbottom = self.rect.midbottom
                self.status = "idle"
                self.frame_index = 0
                # Inicia a invencibilidade!
                self.start_invincibility(duration=120)  # 2 segundos
                return
            self.image = self.shrink_frames[self.frame_index]
            return
        # ==========================================

        if self.is_dead:
            if "death" in self.animations:
                self.image = self.animations["death"][0]
            return

        # Continua a animação normal (crescimento, andar, etc.)
        super().animate()

        if self.is_growing:
            self.grow_timer += 1
            if self.frame_index == 0 and self.grow_timer > 1:
                self.is_growing = False
                self.big = True
                self.status = "idle_big"
                self.frame_index = 0

    def update_image(self):
        image = self.animations[self.status][int(self.frame_index)]

        if self.facing_right:
            self.image = pygame.transform.flip(image, True, False)
        else:
            self.image = image

    def update_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom

    def update(self):
        self.animate()


    def draw(self, surface, camera):
        # ==========================================
        # EFEITO DE PISCAR (durante invencibilidade)
        # ==========================================
        if self.invincible:
            # Alterna entre visível e invisível a cada 2 frames
            if (self.invincible_timer // 2) % 2 == 0:
                return  # Não desenha o player (pisca)
        # ==========================================

        image_rect = self.image.get_rect(midbottom=self.rect.midbottom)
        image_rect = camera.apply(image_rect)
        surface.blit(self.image, image_rect)