from src.game.scenes.menu_scene import MenuScene


class TitleScene(MenuScene):

    def __init__(self, game):
        super().__init__(game)
        self.game.audio.play_music("title")
        self.title = "SUPER MARIO WORLD"
        self.options = ["START GAME"]

    def confirm(self):
        from src.game.scenes.character_select_scene import CharacterSelectScene
        self.game.change_scene(CharacterSelectScene(self.game))
