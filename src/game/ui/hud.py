from src.game.ui.hud_font import HudFont
from src.game.ui.hud_icons import HudIcons
from src.game.settings import START_TIME
from src.game.ui.hud_layout import MARIO_POS, TIME_LABEL_POS, LIVES_POS, RESERVE_BOX_POS, COIN_POS, YOSHI_COIN_POS, \
    SCORE_POS, TIME_VALUE_POS, STAR_POS, LIVES_COUNT_POS, COINS_COUNT_POS


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
        self.font.draw_element(surface, self.player_name, MARIO_POS)

        # ==========================================
        # YOSHI COINS: Desenha um ícone para cada moeda coletada
        # Os ícones aparecem logo após o nome (posição base definida em YOSHI_COIN_POS)
        # ==========================================
        base_x, base_y = YOSHI_COIN_POS  # (130, 20) vindo do hud_layout.py
        for i in range(min(self.player.yoshi_coins, 5)):
            self.font.draw_element(surface, "YOSHI_COIN_ICON", (base_x + i * 18, base_y))
        # ==========================================

        # Outros elementos do HUD
        self.font.draw_element(surface, "TIME", TIME_LABEL_POS)
        self.font.draw_element(surface, "X_LIFE", LIVES_POS)
        self.font.draw_element(surface, "STAR_X", STAR_POS)
        self.font.draw_element(surface, "COIN_X", COIN_POS)

        # Caixa de item reserva
        if self.player.reserve_item is not None:
            self.icons.draw_reserve_box_full(surface, RESERVE_BOX_POS)
        else:
            self.icons.draw_reserve_box(surface, RESERVE_BOX_POS)

        # Números (tempo, vidas, moedas, score)
        self.font.draw_number(surface, self.time, 3, TIME_VALUE_POS, color="gold")
        self.font.draw_number(surface, self.player.lives, 2, LIVES_COUNT_POS)
        self.font.draw_number(surface, self.player.coins, 2, COINS_COUNT_POS)
        self.font.draw_number(surface, self.player.score, 6, SCORE_POS)
