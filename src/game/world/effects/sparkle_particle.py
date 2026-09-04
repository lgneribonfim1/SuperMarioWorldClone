from src.game.world.effects.effect import Effect


class SparkleParticle(Effect):
    def __init__(self, pos, frames, offset=(0, 0), delay=0):

        super().__init__(pos)

        self.frames = [
            frames[0],
            frames[1],
            frames[2],
            frames[1],
            frames[0]
        ]

        self.image = self.frames[0]

        center = (pos[0] + offset[0], pos[1] + offset[1])

        self.rect = self.image.get_rect(center=center)

        self.frame_index = 0
        self.animation_speed = 0.25
        self.delay = delay

    def update(self):
        if self.delay > 0:
            self.delay -= 1
            return

        self.frame_index += self.animation_speed

        if self.frame_index >= len(self.frames):
            self.kill()
            return

        self.image = self.frames[int(self.frame_index)]

        center = self.rect.center
        self.rect = self.image.get_rect(center=center)