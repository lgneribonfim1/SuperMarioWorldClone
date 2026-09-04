import pygame
from src.game.world.block import Block


class RotatingBlock(Block):
    """Bloco que rotaciona ao ser atingido por baixo (fica intangível por um tempo)
    e é destruído pelo pulo girando por cima, gerando 4 destroços."""

    def __init__(self, pos, frames, debris_frames):
        super().__init__(pos, frames)
        self.debris_frames = debris_frames
        self.rotating = False
        self.rotation_timer = 0
        self.rotation_duration = 120  # ~1 segundo
        self.destroyed = False

        # Usado para o estado "intangível"
        self.is_solid = True

    def update(self):
        # Anima a rotação
        if self.rotating:
            self.frame_index += 0.1
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[int(self.frame_index)]

            self.rotation_timer -= 1
            if self.rotation_timer <= 0:
                self.rotating = False
                self.is_solid = True
                self.image = self.frames[0]  # Volta ao frame inicial
        else:
            self.image = self.frames[0]

    def hit(self, level):
        """Chamado quando o jogador bate por baixo."""
        if self.destroyed or self.rotating:
            return

        # Inicia a rotação
        self.rotating = True
        self.rotation_timer = self.rotation_duration
        self.is_solid = False
        level.game.audio.play_sound("bump")

    def resolve_vertical_landing(self, player, prev_rect, previous_ground_tile):
        """Chamado quando o jogador cai sobre o bloco."""
        if self.destroyed or self.rotating:
            return None  # Não é sólido durante a rotação, então não pisa

        # Se o jogador está girando, destrói o bloco
        if player.spinning:
            self.destroy()
            player.direction.y = -10  # Quique para cima (ajuste se quiser mais forte)
            player.spinning = True  # (Opcional) Cancela o giro? No SMW o giro continua. Deixe como preferir.
            return None  # Não pisa, pois o bloco foi destruído

        # Caso contrário, pousa normalmente
        return super().resolve_vertical_landing(player, prev_rect, previous_ground_tile)

    def blocks_horizontal(self):
        # Bloco é sólido horizontalmente (exceto quando rotacionando/destruído)
        return self.is_solid and not self.destroyed

    def blocks_vertical_from_below(self):
        # Bloco é sólido por baixo (exceto quando rotacionando/destruído)
        return self.is_solid and not self.destroyed

    def destroy(self):
        """Cria os 4 destroços e remove o bloco."""
        if self.destroyed:
            return

        self.destroyed = True
        # Cria destroços (serão gerenciados pelo Level)
        from src.game.world.rotating_debris import RotatingDebris
        center = self.rect.center
        # 4 pedaços: esquerda-cima, direita-cima, esquerda-baixo, direita-baixo
        offsets = [(-16, -16), (16, -16), (-16, 16), (16, 16)]
        for offset in offsets:
            debris = RotatingDebris(center, self.debris_frames, offset)
            # Precisa adicionar ao grupo de destroços do Level (vamos criar)
            # O Level terá um grupo `self.debris` ou podemos passar via level
            if hasattr(self, 'level'):
                self.level.debris.add(debris)
            else:
                # Fallback: adiciona ao grupo effects (se não houver grupo específico)
                pass

        self.kill()