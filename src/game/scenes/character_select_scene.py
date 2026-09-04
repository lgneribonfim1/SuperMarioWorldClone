from src.game.scenes.menu_scene import MenuScene


class CharacterSelectScene(MenuScene):

    def __init__(self, game):
        super().__init__(game)
        self.title = "SELECT PLAYER"
        self.options = ["LUIGI", "MARIO"]

    def confirm(self):
        option = self.options[self.selected]
        if option == "LUIGI":
            self.game.selected_character = "luigi"
        elif option == "MARIO":
            self.game.selected_character = "mario"

        from src.game.scenes.overworld_scene import OverworldScene
        self.game.change_scene(OverworldScene(self.game))

    def cancel(self):
        from src.game.scenes.title_scene import TitleScene
        self.game.change_scene(TitleScene(self.game))