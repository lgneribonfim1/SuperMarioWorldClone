import pygame
import os
from src.game.settings import ASSETS_DIR, TILE_SIZE


class GoalBar(pygame.sprite.Sprite):
    def __init__(self, pos, level):
        super().__init__()
        self.level = level
        self.caught = False  # Indica se o jogador já pegou a barra
        self.speed = 2  # Velocidade de subida/descida

        # ==========================================
        # 1. TRANSPARÊNCIA MAGENTA
        # ==========================================
        path_left = os.path.join(ASSETS_DIR, "graphics", "animations", "goal_post_bar_left.png")
        path_right = os.path.join(ASSETS_DIR, "graphics", "animations", "goal_post_bar_right.png")

        self.left_image = pygame.image.load(path_left).convert_alpha()
        self.right_image = pygame.image.load(path_right).convert_alpha()
        self.left_image.set_colorkey((255, 0, 255))
        self.right_image.set_colorkey((255, 0, 255))
        # ==========================================

        # ==========================================
        # 2. DESLOCAMENTO 1 TILE PARA A ESQUERDA
        # ==========================================
        # (Antes começava em pos[0], agora começa em pos[0] - 32 para se alinhar ao poste esquerdo)
        self.rect = pygame.Rect(pos[0] - TILE_SIZE, pos[1], TILE_SIZE * 2, self.left_image.get_height())
        self.hitbox = self.rect.inflate(-8, -8)
        # ==========================================

        # Configuração do loop (Sobe e desce)
        self.start_y = pos[1]
        self.target_y = pos[1] - (7 * TILE_SIZE)
        self.moving_up = False
        self.moving_down = True  # Começa descendo (como no SMW)
        self.rect.y = self.start_y

    def update(self):
        # Se já foi pega, não se move mais e não interage
        if self.caught:
            return

        # ==========================================
        # 3. MOVIMENTO CONTÍNUO (LOOP INFINITO)
        # ==========================================
        if self.moving_down:
            self.rect.y += self.speed
            if self.rect.y >= self.start_y:
                self.rect.y = self.start_y
                self.moving_down = False
                self.moving_up = True

        elif self.moving_up:
            self.rect.y -= self.speed
            if self.rect.y <= self.target_y:
                self.rect.y = self.target_y
                self.moving_up = False
                self.moving_down = True
        # ==========================================

        # Atualiza a hitbox junto com o movimento
        self.hitbox.center = self.rect.center

    def catch(self):
        """Chamado quando o jogador encosta na barra"""
        self.caught = True
        self.kill()
        # NÃO chama self.level.victory() aqui! Isso é responsabilidade
        # exclusiva do sistema de transição em LevelScene agora: Level.update()
        # já seta victory_triggered = True logo depois de chamar catch(), e
        # é o LevelScene.start_transition()/update_transition() quem chama
        # self.level.victory() de verdade, uma única vez, só depois do fade.
        # Chamar aqui também causava uma segunda invocação prematura (antes
        # do fade começar), que trocava a música na hora e construía uma
        # OverworldScene inteira à toa, brigando com a transição de verdade.

    def draw(self, surface, camera):
        # Desenha o lado esquerdo (Tile 1)
        left_rect = camera.apply(pygame.Rect(self.rect.x, self.rect.y, TILE_SIZE, self.rect.height))
        surface.blit(self.left_image, left_rect)

        # Desenha o lado direito (Tile 2)
        right_rect = camera.apply(pygame.Rect(self.rect.x + TILE_SIZE, self.rect.y, TILE_SIZE, self.rect.height))
        surface.blit(self.right_image, right_rect)