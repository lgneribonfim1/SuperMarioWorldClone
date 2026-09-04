import pygame
from src.game.settings import TILE_SIZE, OVERWORLD_PLAYER_SPEED


class OverworldPlayer(pygame.sprite.Sprite):
    """Avatar que anda de célula em célula apenas sobre os caminhos definidos."""

    def __init__(self, start_col, start_row, walkable_cells, frame):
        super().__init__()
        self.walkable_cells = walkable_cells  # set de (col,row) onde pode andar

        self.grid_col = start_col
        self.grid_row = start_row

        self.image = frame
        self.rect = self.image.get_rect()

        self.pixel_pos = pygame.Vector2(
            start_col * TILE_SIZE + TILE_SIZE / 2,
            start_row * TILE_SIZE + TILE_SIZE / 2,
        )
        self.target_pixel_pos = pygame.Vector2(self.pixel_pos)
        self.rect.center = (round(self.pixel_pos.x), round(self.pixel_pos.y))

        self.moving = False
        self.speed = OVERWORLD_PLAYER_SPEED
        self.facing_right = True

    def _try_start_move(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_RIGHT]:
            dx, dy = 1, 0
        elif keys[pygame.K_LEFT]:
            dx, dy = -1, 0
        elif keys[pygame.K_UP]:
            dx, dy = 0, -1
        elif keys[pygame.K_DOWN]:
            dx, dy = 0, 1
        else:
            return

        target_cell = (self.grid_col + dx, self.grid_row + dy)

        # Só pode andar se a célula de destino estiver no conjunto de caminhos
        if target_cell not in self.walkable_cells:
            return

        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

        self.grid_col, self.grid_row = target_cell
        self.target_pixel_pos = pygame.Vector2(
            target_cell[0] * TILE_SIZE + TILE_SIZE / 2,
            target_cell[1] * TILE_SIZE + TILE_SIZE / 2,
        )
        self.moving = True

    def update(self):
        if not self.moving:
            keys = pygame.key.get_pressed()
            self._try_start_move(keys)

        if self.moving:
            delta = self.target_pixel_pos - self.pixel_pos
            dist = delta.length()
            if dist <= self.speed:
                self.pixel_pos = pygame.Vector2(self.target_pixel_pos)
                self.moving = False
            else:
                self.pixel_pos += delta.normalize() * self.speed

            self.rect.center = (round(self.pixel_pos.x), round(self.pixel_pos.y))

    @property
    def current_cell(self):
        return (self.grid_col, self.grid_row)

    def draw(self, surface, camera):
        image = self.image
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        surface.blit(image, camera.apply(self.rect))