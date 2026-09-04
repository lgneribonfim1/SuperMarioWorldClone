import pygame
from src.game.scenes.scene import Scene


class MenuScene(Scene):

    def __init__(self, game):
        super().__init__(game)
        self.title = ""
        self.options = []
        self.selected = 0
        self.title_font = pygame.font.Font(None, 60)
        self.option_font = pygame.font.Font(None, 40)
        self.blink_timer = 0
        self.show_cursor = True

    def update(self):
        self.blink_timer += 1

        if self.blink_timer >= 30:
            self.show_cursor = not self.show_cursor
            self.blink_timer = 0

    def move_up(self):
        self.selected -= 1

        if self.selected < 0:
            self.selected = len(self.options) - 1

    def move_down(self):
        self.selected += 1

        if self.selected >= len(self.options):
            self.selected = 0

    def handle_event(self, event):

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP:
            self.move_up()
        elif event.key == pygame.K_DOWN:
            self.move_down()
        elif event.key == pygame.K_RETURN:
            self.confirm()
        elif event.key == pygame.K_ESCAPE:
            self.cancel()

    def confirm(self):
        pass

    def cancel(self):
        pass

    def draw(self):
        self.game.surface.fill((0, 116, 116))
        title = self.title_font.render(self.title,True,"white")

        title_rect = title.get_rect(center=(256, 80))
        self.game.surface.blit(title, title_rect)
        start_y = 170

        for i, option in enumerate(self.options):
            text = self.option_font.render(option,True,"yellow")
            rect = text.get_rect(center=(256, start_y + i * 40))

            self.game.surface.blit(text, rect)

            if self.show_cursor and i == self.selected:
                cursor = self.option_font.render(">",True,"white")
                cursor_rect = cursor.get_rect(midright=(rect.left - 10, rect.centery))
                self.game.surface.blit(cursor, cursor_rect)
