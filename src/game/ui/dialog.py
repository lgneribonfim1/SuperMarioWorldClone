import pygame


class Dialog:
    def __init__(self, surface, title, options):
        self.surface = surface
        self.title = title
        self.options = options
        self.selected = 0
        self.font = pygame.font.Font(None, 30)

    def draw(self):

        width = 220
        height = 120

        rect = pygame.Rect( 0,0,width,height)
        rect.center = (self.surface.get_width() // 2, self.surface.get_height() // 2)

        pygame.draw.rect(self.surface, (30, 30, 30), rect)
        pygame.draw.rect(self.surface,"white", rect,2)

        title = self.font.render(self.title,True,"white")
        title_rect = title.get_rect(center=(rect.centerx, rect.top + 25))

        self.surface.blit(title, title_rect)

        y = rect.top + 60

        for i, option in enumerate(self.options):
            prefix = "> " if i == self.selected else "  "
            text = self.font.render(prefix + option, True,"white")

            self.surface.blit(text, (rect.left + 25, y))
            y += 28

    def move_up(self):
        if self.selected > 0:
            self.selected -= 1

    def move_down(self):
        if self.selected < len(self.options) - 1:
            self.selected += 1

    def get_selected(self):
        return self.options[self.selected]

