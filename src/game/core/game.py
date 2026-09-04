import pygame
from src.game.ui.dialog import Dialog
from src.game.core.game_state import GameState
from src.game.audio.audio_manager import AudioManager
from src.game.settings import *


class Game:
    def __init__(self, surface, display_screen=None):
        from src.game.scenes.title_scene import TitleScene
        self.surface = surface
        self.display_screen = display_screen or pygame.display.get_surface()
        self.audio = AudioManager()
        self.state = GameState.RUNNING
        self.selected_character = "luigi"
        self.current_scene = TitleScene(self)
        self.quit_dialog = Dialog(self.surface, "QUIT ?", ["YES", "NO"])

        # ==========================================
        # CONTROLE DE PROGRESSO DO OVERWORLD
        # ==========================================
        self.overworld_node_order = []  # Lista de UIDs dos nós na ordem correta
        self.overworld_progress = 0  # Índice do primeiro nível desbloqueado (começa em 0)
        # ==========================================

        # self.coins = 0

        # ADICIONE ESTAS LINHAS
        self.running = True
        self.clock = pygame.time.Clock()

    def change_scene(self, scene):
        self.current_scene = scene

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            if self.state == GameState.RUNNING:
                self.state = GameState.QUIT_MENU
            else:
                self.state = GameState.RUNNING
        elif self.state == GameState.QUIT_MENU:
            if event.key == pygame.K_UP:
                self.quit_dialog.move_up()
            elif event.key == pygame.K_DOWN:
                self.quit_dialog.move_down()
            elif event.key == pygame.K_RETURN:
                if self.quit_dialog.get_selected() == "YES":
                    self.running = False  # MODIFICADO
                    return
                else:
                    self.state = GameState.RUNNING

        if self.state == GameState.RUNNING:
            self.current_scene.handle_event(event)

    def update(self):
        if self.state == GameState.RUNNING:
            self.current_scene.update()
            self.current_scene.draw()

    def draw(self):
        if self.state == GameState.QUIT_MENU:
            self.quit_dialog.draw()
            font = pygame.font.Font(None, 36)
            text = font.render("QUIT ?", True, "white")
            rect = text.get_rect(center=(256, 80))
            self.surface.blit(text, rect)

    # ADICIONE/SUBSTITUA ESTE MÉTODO
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.handle_event(event)

            self.surface.fill((0, 116, 116))
            self.update()
            self.draw()

            scaled_surface = pygame.transform.scale(self.surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.display_screen.blit(scaled_surface, (0, 0))

            pygame.display.update()
            self.clock.tick(FPS)

        return  # Retorna ao menu quando terminar