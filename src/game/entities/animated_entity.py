from src.game.entities.entity import Entity


class AnimatedEntity(Entity):
    def __init__(self):
        super().__init__()
        self.spritesheet = None
        self.animations = {}
        self.status = ""
        self.frame_index = 0
        self.animation_speed = 0.15

    def load_animations(self):
        """
        Cada personagem implementa este método.
        """
        raise NotImplementedError

    def update_image(self):
        """
        Cada personagem decide como mostrar o sprite.
        """
        raise NotImplementedError

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.update_image()