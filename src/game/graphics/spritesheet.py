import pygame


class SpriteSheet:
    def __init__(self, filename, tile_width=16, tile_height=16, transparent_color=(255, 0, 255)):
        self.sheet = pygame.image.load(filename).convert()
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.transparent_color = transparent_color

    def extract(self, x, y, width, height, scale=1):
        rect = pygame.Rect(x, y, width, height)
        image = pygame.Surface((width, height))
        image.blit(self.sheet, (0, 0), rect)

        if self.transparent_color is not None:
            image.set_colorkey(self.transparent_color)

        if scale != 1:
            image = pygame.transform.scale(
                image,
                (width * scale, height * scale)
            )

        return image.convert_alpha()

    def extract_tile(self, row, col, scale=1):
        return self.extract(
            col * self.tile_width,
            row * self.tile_height,
            self.tile_width,
            self.tile_height,
            scale
        )

    def extract_sprite(
            self,
            row,
            col,
            sprite_width,
            sprite_height,
            margin_left=0,
            margin_top=0,
            spacing_x=0,
            spacing_y=0,
            scale=1):

        x = margin_left + col * (sprite_width + spacing_x)
        y = margin_top + row * (sprite_height + spacing_y)

        return self.extract(x,y,sprite_width,sprite_height,scale)

    def extract_sequence(
            self,
            row,
            first_col,
            quantity,
            scale=1):

        frames = []

        for col in range(first_col, first_col + quantity):
            frames.append(self.extract_tile(row, col, scale))

        return frames

    def extract_frames(self, frame_list, scale=1):
        frames = []

        for row, col in frame_list:
            frames.append(self.extract_tile(row, col, scale))

        return frames

    def draw_grid(self, surface, color="red"):
        width = self.sheet.get_width()
        height = self.sheet.get_height()

        for x in range(0, width, self.tile_width):
            pygame.draw.line(surface, color, (x, 0), (x, height))

        for y in range(0, height, self.tile_height):
            pygame.draw.line(surface, color, (0, y), (width, y))

    def extract_tiles(self, positions, scale=1):
        frames = []
        for row, col in positions:
            frames.append(self.extract_tile(row, col, scale))

        return frames


    @property
    def rows(self):
        return self.sheet.get_height() // self.tile_height

    @property
    def cols(self):
        return self.sheet.get_width() // self.tile_width