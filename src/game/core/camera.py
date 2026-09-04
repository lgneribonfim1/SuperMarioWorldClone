import pygame
from src.game.settings import INTERNAL_WIDTH, INTERNAL_HEIGHT


class Camera:
    def __init__(self, world_width: int, world_height: int, world_origin=(0, 0)):
        # Dimensões da tela (usando suas constantes do settings.py)
        self.screen_w = INTERNAL_WIDTH
        self.screen_h = INTERNAL_HEIGHT

        # Limites do mundo
        self.level_w = world_width
        self.level_h = world_height

        # Posição da câmera no mundo (canto superior esquerdo)
        self.x = 0.0
        self.y = 0.0

        self.world_origin = pygame.Vector2(world_origin)
        self.offset = pygame.Vector2()

        # ============================================================
        # CONFIGURAÇÕES DA CÂMERA (Ajuste estes valores ao seu gosto)
        # ============================================================

        # 1. Zona morta e Look-ahead (O segredo do espaço à frente)
        self.dead_zone_w = 120  # Largura da zona morta
        self.dead_zone_h = 160  # Altura da zona morta
        self.look_ahead_max = 80  # Quantos pixels a zona morta desliza para frente
        self.look_ahead_speed = 1.0  # Velocidade que o "olhar" desliza (px/frame)
        self.look_ahead_current = 0.0  # Valor atual do deslocamento
        self.facing = 1  # 1 = direita, -1 = esquerda

        # 2. Suavização horizontal (perseguição contínua até o centro)
        self.h_lerp = 0.1  # 0 a 1: quanto maior, mais "grudado" no centro; menor = mais suave/atrasado

        # 3. Eixo Vertical "Preguiçoso" (Lerp suave)
        self.v_lerp = 0.1  # Suavidade vertical (0 a 1)
        self.v_locked_target = None  # Trava vertical (Só atualiza se sair da zona)

    def _dead_zone_rect(self):
        """Retorna o retângulo da zona morta, SEMPRE fixo e centrado na tela.

        IMPORTANTE: o look-ahead não entra aqui. Se ele deslocasse a dead
        zone (como fazia antes), a borda de gatilho fugiria do jogador
        exatamente enquanto ele acelera, atrasando o início do scroll.
        O look-ahead é aplicado depois, direto em self.x — ele é um efeito
        visual (mostra mais cenário à frente), não faz parte do gatilho.
        """
        rect = pygame.Rect(0, 0, self.dead_zone_w, self.dead_zone_h)
        rect.center = (self.screen_w // 2, self.screen_h // 2)
        return rect

    def update(self, player):
        target_rect = player.rect
        target_vel_x = player.direction.x
        on_ground = player.on_ground

        if target_vel_x > 0.1:
            self.facing = 1
        elif target_vel_x < -0.1:
            self.facing = -1

        moving_fast = abs(target_vel_x) > 0.3
        target_look_ahead = self.facing * self.look_ahead_max if moving_fast else self.look_ahead_current * 0.9

        prev_look_ahead = self.look_ahead_current
        if self.look_ahead_current < target_look_ahead:
            self.look_ahead_current = min(self.look_ahead_current + self.look_ahead_speed, target_look_ahead)
        elif self.look_ahead_current > target_look_ahead:
            self.look_ahead_current = max(self.look_ahead_current - self.look_ahead_speed, target_look_ahead)

        player_screen_y = target_rect.centery - self.y
        dead_zone = self._dead_zone_rect()

        # --- Horizontal: persegue o CENTRO da tela continuamente (suave) ---
        # Sem gatilho liga/desliga: a cada frame a câmera acelera em direção
        # ao ponto onde o player ficaria exatamente centralizado. Isso evita
        # dois problemas: (1) o player preso na borda de uma dead zone larga,
        # e (2) uma correção "tudo ou nada" que causaria saltos visíveis toda
        # vez que ele tocasse a borda. Quando o player está parado, o próprio
        # alvo (desired_x) quase não muda — então a câmera naturalmente já
        # fica quieta, sem precisar de uma dead zone separada para isso.
        desired_x = target_rect.centerx - self.screen_w // 2
        self.x += (desired_x - self.x) * self.h_lerp

        # --- Look-ahead: aplicado como deslocamento extra, suave, sobre self.x ---
        # Só a VARIAÇÃO do look-ahead neste frame é somada — assim ele soma
        # scroll extra na direção que o player está olhando, sem nunca
        # atrasar o gatilho acima.
        self.x += (self.look_ahead_current - prev_look_ahead)

        # --- Eixo Vertical (Estilo "preguiçoso" do SMW) ---
        if player_screen_y < dead_zone.top or player_screen_y > dead_zone.bottom:
            # Saiu da faixa vertical -> recalcula o alvo
            desired_y = target_rect.centery - self.screen_h // 2
            self.v_locked_target = desired_y
        elif on_ground:
            # Pousou no chão -> realinha suavemente (mostra um pouco mais de céu)
            self.v_locked_target = target_rect.bottom - self.screen_h * 0.65

        if self.v_locked_target is not None:
            self.y += (self.v_locked_target - self.y) * self.v_lerp

        # --- Clamp (Limites do mundo) ---
        min_x = self.world_origin.x
        max_x = self.world_origin.x + self.level_w - self.screen_w
        self.x = max(min_x, min(self.x, max_x))

        min_y = self.world_origin.y
        max_y = self.world_origin.y + self.level_h - self.screen_h
        self.y = max(min_y, min(self.y, max_y))

        # Atualiza o offset para o resto do jogo (draw)
        self.offset.x = self.x
        self.offset.y = self.y

    def apply(self, rect):
        return rect.move(-int(self.offset.x), -int(self.offset.y))

    def apply_parallax(self, scroll_factor):
        return self.offset.x * scroll_factor