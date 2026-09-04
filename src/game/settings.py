import os

# Dimensões da tela (proporção retro baseada no SNES expandida)
# ==================================================
# RESOLUÇÃO INTERNA DO JOGO
# ==================================================

INTERNAL_WIDTH = 512
INTERNAL_HEIGHT = 432

# ==================================================
# ESCALA DA JANELA
# ==================================================

SCALE = 1.5

SCREEN_WIDTH = INTERNAL_WIDTH * SCALE
SCREEN_HEIGHT = INTERNAL_HEIGHT * SCALE
TILE_SIZE = 32
FPS = 60

# ==========================================
# CAMINHOS DE PASTAS (CORRIGIDO)
# ==========================================
# Pega a pasta onde este arquivo settings.py está: .../src/game/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Sobe uma pasta para chegar em 'src/'
SRC_DIR = os.path.dirname(BASE_DIR)
# Define a pasta Assets (que está em src/game/assets)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
# Define a pasta de levels
LEVELS_DIR = os.path.join(ASSETS_DIR, 'levels')
# Define a pasta tiles_export
TILES_EXPORT_DIR = os.path.join(ASSETS_DIR, 'tiles_export')
# Define as pastas exportadas do overworld (terrain + ícones de nó)
OVERWORLD_EXPORT_DIR = os.path.join(ASSETS_DIR, 'overworld_export')
OVERWORLD_TERRAIN_DIR = os.path.join(OVERWORLD_EXPORT_DIR, 'terrain')
OVERWORLD_PARTS_DIR = os.path.join(OVERWORLD_EXPORT_DIR, 'parts')

# Física básica
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_FORCE = -11
SLOPE_SLIDE_ACCEL = 0.12  # aceleração/frame do "escorregão" em rampas (dividida pelo friction_mod do tile)
SLOPE_LANDING_DAMPING = 0.2  # fração da vel_x preservada ao pousar numa rampa indo ladeira ACIMA (ver level.py)
SLOPE_CLIMB_SPEED_FACTOR = 0.5  # teto de velocidade ao subir contra a rampa, como fração de target_speed (x friction_mod)
DEBUG_SLOPES = True  # imprime no console o que o motor de colisão "pensa" sobre rampas (ver level.py)

# Overworld (mapa-múndi entre fases)
OVERWORLD_PLAYER_SPEED = 3  # px/frame andando entre células no overworld

# Adicione isso ao final do seu src/settings.py
MARIO_SPRITE_W = 16
MARIO_SPRITE_H = 24

# Pontuação
COIN = 1
COIN_POINTS = 10
GOOMBA_POINTS = 100
KOOPA_POINTS = 200
PIRANHA_POINTS = 200
SPINY_POINTS = 200

# Itens
MUSHROOM_POINTS = 1000
FLOWER_POINTS = 1000
FEATHER_POINTS = 1000
DRAGON_COIN_POINTS = 1000

# Jogo
START_LIVES = 5
START_TIME = 400
COINS_PER_LIFE = 100

# HUD
MAX_SCORE = 999999

# Bônus do poste
GOAL_BONUS = {
    0: 100,
    1: 200,
    2: 400,
    3: 800,
    4: 1000,
    5: 2000,
    6: 4000,
    7: 8000,
}

# ==================================================
# LIMIAR DE MORTE E VITÓRIA
# ==================================================
# Quando o topo do jogador ultrapassar essa coordenada Y, ele morre.
# A altura total do mapa é world_origin.y + world_height.
DEATH_Y_THRESHOLD_OFFSET = 200  # Queda de 200 pixels abaixo do chão do mapa
# Congelamento instantâneo (frame de morte + som já ativos) antes do pulinho
DEATH_FREEZE_DELAY = 60  # 1 segundo a 60 FPS
# Delay do pulinho + queda no vazio, após o congelamento, antes do fade
DEATH_FADE_DELAY = 60  # 1 segundo a 60 FPS
# Impulso vertical do pulinho de morte
DEATH_JUMP_FORCE = -8