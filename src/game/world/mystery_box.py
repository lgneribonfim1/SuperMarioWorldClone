from src.game.world.block import Block

class MysteryBox(Block):
    def __init__(self, pos, frames, used_image, max_hits=1):
        super().__init__(pos, frames)
        self.used_image = used_image
        self.max_hits = max_hits

    def hit(self, level):
        if self.used:
            return

        super().hit(level)      # Faz o bump
        self.register_hit()     # Conta o hit (e muda para usado se atingir max_hits)

        # Cria a moeda subindo (em CADA hit válido)
        from src.game.world.coin_spawn import CoinSpawn
        coin_spawn = CoinSpawn(
            (self.rect.x, self.rect.y - 32),
            level.assets.get_coin_frames(),
            level.game,
            level
        )
        level.effects.add(coin_spawn)