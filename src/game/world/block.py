from src.game.world.animated_tile import AnimatedTile


class Block(AnimatedTile):
    def __init__(self, pos, frames):
        super().__init__(pos, frames)
        self.hitbox = self.rect.inflate(-2, -2)
        self.used = False
        self.bump_offset = 0
        self.original_y = self.rect.y
        self.bumping = False
        self.bump_velocity = 0
        self.max_hits = 1
        self.hit_count = 0
        self.used_image = None
        self.can_bump = False

    def register_hit(self):
        self.hit_count += 1
        if self.hit_count >= self.max_hits:
            self.become_used()

    def start_bump(self):
        if self.bumping:
            return

        self.bumping = True
        self.bump_velocity = -4

    def update_bump(self):
        if not self.bumping:
            return

        self.rect.y += self.bump_velocity
        self.bump_velocity += 1
        if self.rect.y >= self.original_y:
            self.rect.y = self.original_y
            self.bump_velocity = 0
            self.bumping = False

    def update(self):
        super().update()
        self.update_bump()

    def hit(self, level):
        level.game.audio.play_sound("bump")
        if self.used and not self.can_bump:
            return

        self.start_bump()

    def become_used(self):
        if self.used_image is None:
            return

        self.used = True
        self.frames = [self.used_image]
        self.frame_index = 0
        self.image = self.used_image

    # ------------------------------------------------------------
    # INTERFACE DE COLISÃO (mesma usada por Tile/SlopeTile em tile.py)
    # ------------------------------------------------------------
    # Block (e por herança MysteryBox/YellowBox) vive num grupo separado
    # (self.blocks) que Level._get_nearby_tiles() mistura com os tiles
    # normais — então precisa da MESMA interface polimórfica que Tile
    # define, senão Level.horizontal_movement_collision /
    # vertical_movement_collision quebram ao chamar esses métodos nele.
    def blocks_horizontal(self):
        return True  # bloco é sempre sólido dos lados

    def blocks_vertical_from_below(self):
        return True  # é assim que o player "bate" no bloco por baixo (ver hit())

    def resolve_vertical_landing(self, player, prev_rect, previous_ground_tile):
        # Mesma proteção contra teleporte usada em Tile.resolve_vertical_landing:
        # só pousa em cima se não estava atravessando por dentro no frame
        # anterior (na prática, blocos bloqueiam nos outros eixos também,
        # então isso raramente dispara — mas evita tunneling em quedas
        # muito rápidas/frames pulados, e mantém a mesma regra em todo
        # lugar que implementa essa interface).
        was_overlapping = self.rect.colliderect(prev_rect)
        was_grounded_here = previous_ground_tile is self
        if was_overlapping and not was_grounded_here:
            return None
        player.rect.bottom = self.rect.top
        player.direction.y = 0
        return self