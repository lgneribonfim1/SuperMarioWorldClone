from src.game.ui.hud_font import HudFont
from src.game.ui.hud_icons import HudIcons
from src.game.settings import START_TIME
from src.game.ui.hud_layout import YOSHI_COIN_POS


class HUD:

    def __init__(self, character, player):
        self.font = HudFont()
        self.icons = HudIcons()
        self.player = player
        self.player_name = character.upper()
        self.time = START_TIME
        self.time_counter = 0

    def update(self):
        self.time_counter += 1
        if self.time_counter >= 60:
            self.time_counter = 0
            if self.time > 0:
                self.time -= 1

    def draw(self, surface):
        # Desenha o nome do personagem
        self.font.draw_element(surface, self.player_name, (40, 22))

        # ==========================================
        # YOSHI COINS: Desenha um ícone para cada moeda coletada
        # Os ícones aparecem logo após o nome (posição base definida em YOSHI_COIN_POS)
        # ==========================================
        base_x, base_y = YOSHI_COIN_POS  # (200, 24) vindo do hud_layout.py
        for i in range(min(self.player.yoshi_coins, 5)):
            self.font.draw_element(surface, "YOSHI_COIN_ICON", (base_x + i * 18, base_y))
        # ==========================================

        # Outros elementos do HUD
        self.font.draw_element(surface, "TIME", (305, 22))
        self.font.draw_element(surface, "X_LIFE", (56, 38))
        self.font.draw_element(surface, "STAR_X", (145, 38))
        self.font.draw_element(surface, "COIN_X", (400, 24))

        # Caixa de item reserva
        if self.player.reserve_item is not None:
            self.icons.draw_reserve_box_full(surface, (224, 10))
        else:
            self.icons.draw_reserve_box(surface, (224, 10))

        # Números (tempo, vidas, moedas, score)
        self.font.draw_number(surface, self.time, 3, (305, 40), color="gold")
        self.font.draw_number(surface, self.player.lives, 2, (72, 38))
        self.font.draw_number(surface, self.player.coins, 2, (464, 24))
        self.font.draw_number(surface, self.player.score, 6, (400, 40))

        # REMOVIDO: A linha do contador numérico de Yoshi Coins
        # self.font.draw_number(surface, self.player.yoshi_coins, 1, (290, 38), color="gold")