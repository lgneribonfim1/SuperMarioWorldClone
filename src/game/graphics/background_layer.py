from src.game.core.game_object import GameObject


class BackgroundLayer(GameObject):
    def __init__(self, image, scroll_factor=0.0):
        super().__init__()

        self.image = image
        self.scroll_factor = scroll_factor

    def draw(self, surface, camera):
        offset_x = camera.apply_parallax(self.scroll_factor)
        image_width = self.image.get_width()

        # Mantém o deslocamento sempre entre 0 e image_width
        start_x = -(offset_x % image_width)
        x = start_x

        while x < surface.get_width():
            y = surface.get_height() - self.image.get_height()
            surface.blit(self.image, (x, y))
            x += image_width