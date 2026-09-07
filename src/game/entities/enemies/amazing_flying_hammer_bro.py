import pygame
from src.game.entities.enemy import Enemy
from src.game.entities.enemies.hammer import Hammer


class AmazingFlyingHammerBro(Enemy):
    def __init__(self, pos, frame_sets, hammer_frames, game,
                 wing_frames=None, throw_cooldown=90):
        super().__init__(pos, frame_sets["left"])
        self.game = game

        self.left_frames = frame_sets["left"]
        self.right_frames = frame_sets["right"]
        self.hammer_frames = hammer_frames
        self.wing_frames = wing_frames

        self.throw_cooldown = throw_cooldown
        self.throw_timer = throw_cooldown

        # Direção do arremesso (será atualizada para olhar para o jogador)
        self.direction.x = -1  # Inicial (mas será sobrescrito)
        self.facing_right = False

        self.state = "flying"
        self.animation_speed = 0.1
        self.wing_frame_index = 0

        # Hitbox de 32x32, alinhada ao topo do corpo (onde Mario pisa)
        self.hitbox = pygame.Rect(0, 0, 32, 32)
        self.hitbox.midtop = (self.rect.centerx, self.rect.top)

    def _update_facing_to_player(self, player):
        """Vira o corpo do AFHB para a direção do jogador."""
        if player.rect.centerx > self.rect.centerx:
            self.direction.x = 1
            self.facing_right = True
        else:
            self.direction.x = -1
            self.facing_right = False

    def _throw_hammer(self, level, player):
        # Atualiza a direção antes de arremessar (caso o jogador tenha se movido)
        self._update_facing_to_player(player)

        hammer = Hammer(
            (self.rect.centerx - 16, self.rect.centery -32),
            self.hammer_frames,
            self.direction.x,
            self.game
        )
        if hasattr(level, 'enemy_projectiles'):
            level.enemy_projectiles.add(hammer)

    def animate(self):
        # Usa o facing_right para escolher o frame correto (esquerda ou direita)
        frame_list = self.right_frames if self.facing_right else self.left_frames
        self.image = frame_list[0]

        if self.facing_right:
            # A spritesheet já tem o frame pronto para a direita, mas se
            # preferir usar o espelhamento, pode descomentar a linha abaixo:
            # self.image = pygame.transform.flip(self.image, True, False)
            pass

        # Animação das asas (controlada pela plataforma, mas mantida aqui por segurança)
        self.wing_frame_index += self.animation_speed * 2
        if self.wing_frame_index >= 2:
            self.wing_frame_index = 0

    def _hurt_player(self, player):
        if player.invincible:
            return
        elif player.big:
            player.shrink()
        else:
            if hasattr(player, 'level') and player.level:
                player.level.death_triggered = True
                player.die()

    def update(self, player, prev_player_rect=None, prev_player_hitbox=None):
        if not self.alive:
            return

        level = player.level if hasattr(player, 'level') else None

        # Mantém o corpo sempre olhando para o jogador
        self._update_facing_to_player(player)

        self.animate()
        self.throw_timer -= 1
        if self.throw_timer <= 0 and level:
            self._throw_hammer(level, player)  # Passa o player para mirar
            self.throw_timer = self.throw_cooldown

        self.hitbox.midtop = (self.rect.centerx, self.rect.top)

        if self.hitbox.colliderect(player.hitbox):
            is_stomp = (player.direction.y > 0 and
                        prev_player_rect is not None and
                        prev_player_rect.bottom <= self.rect.top + 10)

            if is_stomp:
                self.kill()
                player.direction.y = -8
                self.game.audio.play_sound("stomp")
            else:
                self._hurt_player(player)

    def draw(self, surface, camera):
        if not self.alive:
            return

        cx = self.rect.centerx
        top_y = self.rect.top

        # Apenas o corpo (as asas são desenhadas pela plataforma)
        body_rect = self.image.get_rect(midbottom=(cx, top_y + 32))
        surface.blit(self.image, camera.apply(body_rect))