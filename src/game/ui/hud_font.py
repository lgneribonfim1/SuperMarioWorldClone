from src.game.graphics.spritesheet import SpriteSheet


class HudFont:
    def __init__(self):
        self.sheet = SpriteSheet(
            "assets/graphics/HUD/fonts_tilesets8x8.png",
            tile_width=8,
            tile_height=8,
            transparent_color=(255, 0, 255)
        )

        self.sparkle_frames = [
            self.sheet.extract_tile(3, 12, scale=2),
            self.sheet.extract_tile(3, 13, scale=2),
            self.sheet.extract_tile(3, 14, scale=2)
        ]

        self.elements = {}
        self.white_digits = {}
        self.gold_digits = {}
        self.load_elements()
        self.load_white_digits()
        self.load_gold_digits()

    def load_white_digits(self):
        for i in range(10):
            self.white_digits[str(i)] = self.sheet.extract_tile(row=3, col=i, scale=2)

    def load_gold_digits(self):
        for i in range(10):
            self.gold_digits[str(i)] = self.sheet.extract_tile(row=2, col=5 + i, scale=2)

    def get_sparkle_frames(self):
        return self.sparkle_frames

    def load_element(self, name, row, first_col, quantity):
        tiles = []
        for col in range(first_col, first_col + quantity):
            tiles.append(self.sheet.extract_tile(row, col, scale=2))

        self.elements[name] = tiles

    def load_elements(self):
        self.load_element("TIME", 0, 2, 3)
        self.load_element("MARIO", 0, 8, 5)
        self.load_element("LUIGI", 1, 8, 5)
        self.load_element("X_LIFE", 0, 1, 1)
        self.load_element("STAR_X", 0, 0, 2)
        self.load_element("COIN_X", 0, 5, 2)
        self.load_element("YOSHI_COIN_ICON", 0, 5, 1)

    def get_element(self, element):

        return self.elements[element]

    def draw_element(self, surface, element, position):
        x, y = position
        for tile in self.get_element(element):
            surface.blit(tile, (x, y))
            x += tile.get_width()

    def draw_number(self, surface, value, digits, position, color="white"):
        if color == "gold":
            digit_set = self.gold_digits
        else:
            digit_set = self.white_digits
        value = str(value)

        digit_width = next(iter(digit_set.values())).get_width()

        x, y = position
        x += (digits - len(value)) * digit_width

        for digit in value:
            surface.blit(digit_set[digit], (x, y))

            x += digit_width