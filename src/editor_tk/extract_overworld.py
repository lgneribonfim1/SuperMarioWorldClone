import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DIR = os.path.join(BASE_DIR, 'game')
ASSETS_DIR = os.path.join(GAME_DIR, 'assets', 'graphics', 'overworld', 'tilesets')
OUTPUT_DIR = os.path.join(GAME_DIR, 'assets', 'overworld_export')

TERRAIN_DIR = os.path.join(OUTPUT_DIR, 'terrain')
NODES_DIR = os.path.join(OUTPUT_DIR, 'nodes')

SOURCE_SIZE = 16  # Seus tiles são 16x16
TARGET_SIZE = 32  # Tamanho usado pelo jogo (TILE_SIZE)

os.makedirs(TERRAIN_DIR, exist_ok=True)
os.makedirs(NODES_DIR, exist_ok=True)

def extract_overworld():
    # 1. Processar o Tileset de Terreno (overworld_tiles.png)
    terrain_path = os.path.join(ASSETS_DIR, "overworld_forest_tileset.png")
    if os.path.exists(terrain_path):
        print("Extraindo terreno (overworld_tiles.png)...")
        sheet = Image.open(terrain_path)
        cols = sheet.width // SOURCE_SIZE
        rows = sheet.height // SOURCE_SIZE

        for row in range(rows):
            for col in range(cols):
                x = col * SOURCE_SIZE
                y = row * SOURCE_SIZE
                tile = sheet.crop((x, y, x + SOURCE_SIZE, y + SOURCE_SIZE))
                tile = tile.resize((TARGET_SIZE, TARGET_SIZE), Image.Resampling.NEAREST)
                tile.save(os.path.join(TERRAIN_DIR, f"terrain_{row}_{col}.png"))
        print(f"Terreno salvo em: {TERRAIN_DIR}")
    else:
        print("Arquivo overworld_tiles.png não encontrado.")

    # 2. Processar o Tileset de Nós (overworld_nodes.png)
    nodes_path = os.path.join(ASSETS_DIR, "overworld_nodes.png")
    if os.path.exists(nodes_path):
        print("Extraindo nós (overworld_nodes.png)...")
        sheet = Image.open(nodes_path)
        cols = sheet.width // SOURCE_SIZE
        rows = sheet.height // SOURCE_SIZE

        for row in range(rows):
            for col in range(cols):
                x = col * SOURCE_SIZE
                y = row * SOURCE_SIZE
                tile = sheet.crop((x, y, x + SOURCE_SIZE, y + SOURCE_SIZE))
                tile = tile.resize((TARGET_SIZE, TARGET_SIZE), Image.Resampling.NEAREST)
                tile.save(os.path.join(NODES_DIR, f"node_{row}_{col}.png"))
        print(f"Nós salvos em: {NODES_DIR}")
    else:
        print("Arquivo overworld_nodes.png não encontrado.")

if __name__ == "__main__":
    extract_overworld()