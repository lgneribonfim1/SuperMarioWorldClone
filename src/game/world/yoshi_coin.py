from src.game.world.animated_tile import AnimatedTile
from src.game.resources.effects.effect_assets import effects_assets
from src.game.world.effects.sparkle_particle import SparkleParticle


class YoshiCoin(AnimatedTile):
    def __init__(self, pos, frames, game):
        # A moeda Yoshi é 32x64, então a hitbox é maior
        super().__init__(pos, frames)
        self.game = game
        self.hitbox = self.rect.inflate(-12, -12)
        self.collected = False

    def collect(self, level):
        # Efeito de brilho (reutiliza o do coin.py)
        level.effects.add(
            SparkleParticle(self.rect.center, effects_assets.get_sparkle(), offset=(0, -8), delay=0),
            SparkleParticle(self.rect.center, effects_assets.get_sparkle(), offset=(8, 0), delay=3),
            SparkleParticle(self.rect.center, effects_assets.get_sparkle(), offset=(0, 8), delay=6),
            SparkleParticle(self.rect.center, effects_assets.get_sparkle(), offset=(-8, 0), delay=9)
        )

        level.game.audio.play_sound("dragon_coin")
        player = level.player.sprite

        # Chama o método dedicado que trata a lógica de 5 moedas + 1UP
        player.add_yoshi_coin()
        self.kill()

    def update(self):
        super().update()
        self.hitbox.center = self.rect.center