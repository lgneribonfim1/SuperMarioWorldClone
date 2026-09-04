import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'game', 'assets', 'graphics', 'tilesets')
OUTPUT_DIR = os.path.join(BASE_DIR, 'game', 'assets', 'tiles_export')
TILE_SIZE = 16

os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_all():
    files = [f for f in os.listdir(ASSETS_DIR) if f.endswith('.png')]
    print(f"Extraindo {len(files)} tilesets...")

    for filename in files:
        path = os.path.join(ASSETS_DIR, filename)
        sheet = Image.open(path)
        cols = sheet.width // TILE_SIZE
        rows = sheet.height // TILE_SIZE

        for row in range(rows):
            for col in range(cols):
                tile = sheet.crop((col * 16, row * 16, col * 16 + 16, row * 16 + 16))
                tile = tile.resize((32, 32), Image.Resampling.NEAREST)
                name = f"{filename.replace('.png', '')}_{row}_{col}.png"
                tile.save(os.path.join(OUTPUT_DIR, name))
    print("Extração concluída!")


if __name__ == "__main__":
    extract_all()