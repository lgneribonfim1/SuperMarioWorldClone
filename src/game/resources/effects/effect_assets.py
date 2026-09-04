from src.game.graphics.spritesheet import SpriteSheet


class EffectAssets:

    def __init__(self):

        sheet = SpriteSheet(
            "assets/graphics/HUD/fonts_tilesets8x8.png",
            tile_width=8,
            tile_height=8,
            transparent_color=(255, 0, 255)
        )

        self.sparkle_frames = [
            sheet.extract_tile(3, 12, scale=2),
            sheet.extract_tile(3, 13, scale=2),
            sheet.extract_tile(3, 14, scale=2)
        ]
    def get_sparkle(self):
        return self.sparkle_frames

effects_assets = EffectAssets()