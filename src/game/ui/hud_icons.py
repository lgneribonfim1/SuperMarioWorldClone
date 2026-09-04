from src.game.graphics.spritesheet import SpriteSheet


class HudIcons:

    def __init__(self):

        self.sheet = SpriteSheet(
            "assets/graphics/HUD/HUD_objects_tileset.png",
            tile_width=16,
            tile_height=16,
            transparent_color=(255, 0, 255)
        )

        self.reserve_box = [
            [
                self.sheet.extract_tile(0, 0, scale=2),
                self.sheet.extract_tile(0, 1, scale=2)
            ],
            [
                self.sheet.extract_tile(1, 0, scale=2),
                self.sheet.extract_tile(1, 1, scale=2)
            ]
        ]

        self.reserve_box_full = [
            [
                self.sheet.extract_tile(0, 2, scale=2),
                self.sheet.extract_tile(0, 3, scale=2)
            ],
            [
                self.sheet.extract_tile(1, 2, scale=2),
                self.sheet.extract_tile(1, 3, scale=2)
            ]
        ]

    def draw_reserve_box(self, surface, position):
        x, y = position
        tile_size = 32  # 16 px × escala 2
        for row in range(2):
            for col in range(2):
                surface.blit(
                    self.reserve_box[row][col],
                    (
                        x + col * tile_size,
                        y + row * tile_size
                    )
                )

    def draw_reserve_box_full(self, surface, position):
        x, y = position
        tile_size = 32
        for row in range(2):
            for col in range(2):
                surface.blit(
                    self.reserve_box_full[row][col],
                    (
                        x + col * tile_size,
                        y + row * tile_size
                    )
                )