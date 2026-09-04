import pygame
from src.game.scenes.scene import Scene
from src.game.world.level import Level


class LevelScene(Scene):

    def __init__(self, game, level_filename="map_1.json", return_cell=None, node_uid=None, music="overworld"):
        super().__init__(game)
        self.level = Level(
            game, game.surface, game.selected_character,
            level_filename=level_filename,
            return_cell=return_cell,
            node_uid=node_uid,
            music=music
        )

        # Estados de transição
        self.transition_active = False
        self.transition_type = None  # "death" ou "victory"
        self.transition_timer = 0
        self.transition_duration = 360  # frames (1 segundo a 60 FPS)
        self.transition_callback = None
        self.fade_surface = pygame.Surface(self.game.surface.get_size())
        self.fade_surface.fill((0, 0, 0))

        # =======================================================
        # TOCA A MÚSICA DA FASE RECEBIDA DO NÓ
        # =======================================================
        if music:
            self.game.audio.play_music(music)
        # =======================================================

    def start_transition(self, transition_type, callback):
        if self.transition_active:
            return
        self.transition_active = True
        self.transition_type = transition_type
        self.transition_timer = 0
        self.transition_callback = callback

        # Toca o som apropriado
        #if transition_type == "death":
            #self.game.audio.play_sound("lost_a_life")  # certifique-se de ter esse som
        if transition_type == "victory":
            self.game.audio.play_sound("course_clear")  # e este também

    def update_transition(self):
        self.transition_timer += 1
        if self.transition_timer >= self.transition_duration:
            self.transition_active = False
            if self.transition_callback:
                result = self.transition_callback()  # para vitória, retorna a cena; para morte, None
                print(f"[DEBUG] resultado do callback: {result}")
                if result is not None:
                    print("[DEBUG] chamando change_scene")
                    self.game.change_scene(result)  # só troca se veio uma cena
            self.transition_callback = None
            self.transition_type = None

    def handle_event(self, event):
        pass

    def update(self):
        if self.transition_active:
            self.update_transition()
        else:
            self.level.update()

            # ==========================================
            # VERIFICA SE A MORTE TERMINOU (após o pulo)
            # ==========================================
            if self.level.death_complete:
                self.level.death_complete = False  # Reseta a flag
                self.start_transition("death", self.level.reset_level)
            elif self.level.victory_triggered:
                self.level.victory_triggered = False
                self.start_transition("victory", self.level.victory)

    def draw(self):
        self.level.draw()

        if self.transition_active:
            # Calcula o alpha com base no tempo
            progress = self.transition_timer / self.transition_duration
            alpha = int(min(progress * 255, 255))
            self.fade_surface.set_alpha(alpha)
            self.game.surface.blit(self.fade_surface, (0, 0))