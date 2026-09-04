import pygame
from src.game.world.mushroom import Mushroom


class MushroomSpawn(pygame.sprite.Sprite):
    def __init__(self, pos, mushroom_image, level):
        super().__init__()
        self.image = mushroom_image
        self.rect = self.image.get_rect(topleft=pos)
        self.start_y = pos[1]
        self.level = level

        # Velocidade de subida (começa rápido e desacelera)
        self.vel_y = -1
        self.finished = False

        self.level.game.audio.play_sound("sprout")

    def update(self):
        if self.finished:
            return

        # Sobe devagar e desacelera até parar
        self.rect.y += self.vel_y
        self.vel_y += 0.03

        # Quando atingir o topo (32 pixels acima do início)
        if self.rect.y <= self.start_y - 12:
            self.finish()

    def finish(self):
        self.finished = True

        # Toca o som de "sprout"
        # self.level.game.audio.play_sound("sprout")

        # Cria o cogumelo verdadeiro (agora ele vai nascer "pronto" no topo)
        mushroom = Mushroom((self.rect.x, self.rect.y), self.image)
        self.level.mushrooms.add(mushroom)

        self.kill()

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))