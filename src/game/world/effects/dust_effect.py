from src.game.world.effects.effect import Effect


class DustEffect(Effect):
    """
    Efeito de poeira. Anima os frames uma única vez e se auto-destrói.
    Usado em pulos, aterrissagens e corridas.

    Os frames devem vir JÁ na ordem de exibição (2 -> 1 -> 0),
    pois o asset_manager é quem cuida da reversão.
    """

    def __init__(self, pos, frames, offset=(0, 0), animation_speed=0.3):
        super().__init__(pos)

        self.frames = frames
        self.image = self.frames[0]

        # Posiciona o efeito com base no offset
        center = (pos[0] + offset[0], pos[1] + offset[1])
        self.rect = self.image.get_rect(center=center)

        self.frame_index = 0
        self.animation_speed = animation_speed

    def update(self):
        self.frame_index += self.animation_speed

        if self.frame_index >= len(self.frames):
            self.kill()
            return

        self.image = self.frames[int(self.frame_index)]

        # Mantém o centro fixo ao trocar de frame (evita "pular")
        center = self.rect.center
        self.rect = self.image.get_rect(center=center)