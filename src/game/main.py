import pygame
import sys
import subprocess
import os
from src.game.settings import *
from src.game.core.game import Game


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.options = ["Play Game", "Level Editor", "Overworld Editor", "Quit"]
        self.selected = 0
        self.font = pygame.font.Font(None, 48)
        self.running = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected]
        return None

    def draw(self):
        self.screen.fill((0, 0, 0))

        # Título
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("SUPER MARIO WORLD", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)

        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.selected else (100, 100, 100)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 60))
            self.screen.blit(text, rect)

        # Instruções
        small_font = pygame.font.Font(None, 24)
        instructions = small_font.render("Use UP/DOWN to select, ENTER to choose", True, (150, 150, 150))
        instr_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(instructions, instr_rect)

        pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario World")
    clock = pygame.time.Clock()

    game_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

    while True:
        menu = MainMenu(screen)

        while menu.running:
            choice = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                choice = menu.handle_event(event)

            if choice == "Play Game":
                # Inicia o jogo
                game = Game(game_surface, screen)
                game.run()
                # Quando o jogo terminar, recria o menu
                break
            elif choice == "Level Editor":
                # Fecha a janela do Pygame (o jogo atual)
                pygame.quit()

                # ==========================================================
                # Lógica Infalível para achar o caminho do Editor Tkinter
                # ==========================================================
                # 1. Pega onde este arquivo main.py está: .../SuperMario/src/game/
                current_dir = os.path.dirname(os.path.abspath(__file__))

                # 2. Sobe duas pastas para chegar na raiz do projeto (SuperMario/)
                project_root = os.path.dirname(os.path.dirname(current_dir))

                # 3. Desce até o arquivo do editor: .../SuperMario/src/editor_tk/editor_app.py
                editor_path = os.path.join(project_root, 'src', 'editor_tk', 'editor_app.py')
                # ==========================================================

                # Abre o editor Tkinter em um processo separado
                subprocess.Popen([sys.executable, editor_path])

                # Encerra o processo do jogo (para não ficar travado em segundo plano)
                sys.exit()

            elif choice == "Overworld Editor":
                # Mesma lógica do "Level Editor" acima, só que aponta pro
                # editor de overworld em vez do editor de fases.
                pygame.quit()

                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
                overworld_editor_path = os.path.join(project_root, 'src', 'editor_tk', 'overworld_editor_map.py')

                subprocess.Popen([sys.executable, overworld_editor_path])
                sys.exit()

            elif choice == "Quit":
                pygame.quit()
                sys.exit()

            menu.draw()
            clock.tick(60)


if __name__ == "__main__":
    main()