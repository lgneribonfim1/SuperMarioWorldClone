from src.game.world.block import Block
# Importa a nova classe de spawn
from src.game.world.mushroom_spawn import MushroomSpawn


class YellowBox(Block):
    def __init__(self, pos, frames, used_image, mushroom_image):
        super().__init__(pos, frames)
        self.used_image = used_image
        self.mushroom_image = mushroom_image
        self.has_spawned = False

    def hit(self, level):
        super().hit(level)
        if self.used:
            return

        self.register_hit()
        if self.used and not self.has_spawned:
            self.has_spawned = True
            from src.game.world.mushroom_spawn import MushroomSpawn
            # Agora a imagem do cogumelo vem do AssetManager do Level
            mushroom_spawn = MushroomSpawn(
                (self.rect.x, self.rect.y - 32),
                level.assets.get_mushroom_image(),
                level
            )
            level.effects.add(mushroom_spawn)