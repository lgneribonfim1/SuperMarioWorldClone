from src.game.graphics.spritesheet import SpriteSheet


class EffectAssets:

    def __init__(self):
        # Spritesheet para efeitos do player (ex: stomp)
        self.player_effect_sheet = SpriteSheet(
            "assets/graphics/sprites/player_effects.png",
            tile_width=16,
            tile_height=16,
            transparent_color=(255, 0, 255)
        )

        # Carrega o frame de stomp (linha 0, coluna 4), escala x2
        self.stomp_frame = self.player_effect_sheet.extract_tile(row=0, col=4, scale=2)

        # Spritesheet para sparkle (HUD font)
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

    def get_stomp(self):
        return self.stomp_frame


effects_assets = EffectAssets()