from src.game.world.animated_tile import AnimatedTile
from src.game.resources.effects.effect_assets import effects_assets
from src.game.world.effects.sparkle_particle import SparkleParticle


class Coin(AnimatedTile):
    def __init__(self, pos, frames, game):
        super().__init__(pos, frames)
        self.game = game
        self.hitbox = self.rect.inflate(-14, -14)
        self.collected = False
        self.particles = []

    def collect(self, level):
        level.effects.add(
            SparkleParticle(self.rect.center,effects_assets.get_sparkle(),offset=(0, -8),delay=0),
            SparkleParticle(self.rect.center,effects_assets.get_sparkle(),offset=(8, 0),delay=3),
            SparkleParticle(self.rect.center,effects_assets.get_sparkle(),offset=(0, 8),delay=6),
            SparkleParticle(self.rect.center,effects_assets.get_sparkle(),offset=(-8, 0),delay=9)
        )

        level.game.audio.play_sound("coin")
        player = level.player.sprite
        player.add_coin()
        self.kill()

    def update(self):
        super().update()
        self.hitbox.center = self.rect.center