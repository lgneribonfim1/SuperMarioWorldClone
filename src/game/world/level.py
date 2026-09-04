import pygame
import json
from src.game.settings import *
from src.game.core.camera import Camera
from src.game.core.asset_manager import AssetManager
from src.game.graphics.background_layer import BackgroundLayer
from src.game.ui.hud import HUD
from src.game.world.level_builder import LevelBuilder
from src.game.world.physics_system import PhysicsSystem


class Level:
    def __init__(self, game, surface, character, level_filename="map_1.json", return_cell=None,
                 node_uid=None, music="overworld"):
        self.game = game
        self.display_surface = surface
        self.return_node_uid = node_uid
        self.return_music = music
        self.character = character

        # Grupos de sprites
        self.tiles = pygame.sprite.Group()
        self.back_tiles = pygame.sprite.Group()
        self.front_tiles = pygame.sprite.Group()
        self.collision_tiles = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.mushrooms = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        self.collectables = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.enemies = pygame.sprite.Group()
        self.fireballs = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.back_decoration_tiles = pygame.sprite.Group()
        self.front_decoration_tiles = pygame.sprite.Group()
        self.debris = pygame.sprite.Group()
        self.reserve_items = pygame.sprite.Group()

        # Portal (Meta do nível)
        self.goal_sprite = None
        self.level_complete = False
        self.death_triggered = False
        self.death_complete = False
        self.death_timer = 0
        self.victory_triggered = False

        self.level_filename = level_filename
        self.return_cell = return_cell

        # Caminhos
        self.level_file = os.path.join(LEVELS_DIR, level_filename)

        # Carrega os assets
        self.assets = AssetManager()
        self.assets.load_tile_images()

        # Carrega o JSON
        try:
            with open(self.level_file, 'r') as f:
                self.level_data = json.load(f)
        except FileNotFoundError:
            print(f"ERRO: Arquivo de nível '{self.level_file}' não encontrado!")
            self.level_data = {"width": 50, "height": 20}
        except json.JSONDecodeError:
            print(f"ERRO: Arquivo '{self.level_file}' corrompido ou inválido!")
            self.level_data = {"width": 50, "height": 20}

        self.level_w = self.level_data["width"] * TILE_SIZE
        self.level_h = self.level_data["height"] * TILE_SIZE
        self.world_origin = pygame.Vector2(0, INTERNAL_HEIGHT - self.level_h)
        self.camera = Camera(self.level_w, self.level_h, self.world_origin)
        self.physics = PhysicsSystem(self.world_origin)

        # ==========================================
        # CONSTRUÇÃO DO MUNDO (Delegate para o Builder)
        # ==========================================
        builder = LevelBuilder(self.game, self.level_data, self.world_origin, self.assets,
                               self.character, self)
        built = builder.build()

        self.tiles = built["tiles"]
        self.back_tiles = built["back_tiles"]
        self.front_tiles = built["front_tiles"]
        self.collision_tiles = built["collision_tiles"]
        self.blocks = built["blocks"]
        self.mushrooms = built["mushrooms"]
        self.collectables = built["collectables"]
        self.player = built["player_group"]
        self.enemies = built["enemies"]
        self.fireballs = built["fireballs"]
        self.goal_sprite = built["goal_sprite"]
        self.platforms = built["platforms"]
        self.back_decoration_tiles = built["back_decoration_tiles"]
        self.front_decoration_tiles = built["front_decoration_tiles"]
        self.debris = built["debris"]
        self.reserve_items = built["reserve_items"]
        # ==========================================

        # Background
        self.background = BackgroundLayer(self.assets.get_background_image(), scroll_factor=0.2)

        self.hud = HUD(self.character, self.player.sprite)


    def collect_coins(self):
        player = self.player.sprite
        for coin in self.collectables:
            if player.hitbox.colliderect(coin.hitbox):
                coin.collect(self)

    def draw(self):
        self.background.draw(self.display_surface, self.camera)

        # ORDEM DE RENDERIZAÇÃO (Z-Order)
        for decoration in self.back_decoration_tiles:
            decoration.draw(self.display_surface, self.camera)

        for tile in self.back_tiles:
            tile.draw(self.display_surface, self.camera)

        # 2. Camada do Meio (Inimigos, Tiles, Blocos e Fireballs)
        for obj in self.collectables:
            obj.draw(self.display_surface, self.camera)

        for enemy in self.enemies:
            enemy.draw(self.display_surface, self.camera)

        for platform in self.platforms:
            platform.draw(self.display_surface, self.camera)

        for tile in self.tiles:
            tile.draw(self.display_surface, self.camera)

        for block in self.blocks:
            block.draw(self.display_surface, self.camera)

        # FIREBALLS AGORA SÃO DESENHADAS DEPOIS DO TERRENO
        for fireball in self.fireballs:
            fireball.draw(self.display_surface, self.camera)

        for mushroom in self.mushrooms:
            mushroom.draw(self.display_surface, self.camera)

        for effect in self.effects:
            effect.draw(self.display_surface, self.camera)
        self.player.sprite.draw(self.display_surface, self.camera)

        # Desenha o Portal (Goal Bar)
        if self.goal_sprite:
            self.goal_sprite.draw(self.display_surface, self.camera)

        for decoration in self.front_decoration_tiles:
            decoration.draw(self.display_surface, self.camera)

        # 3. Camada da Frente (Poste Direito)
        for tile in self.front_tiles:
            tile.draw(self.display_surface, self.camera)

        for debris in self.debris:
            debris.draw(self.display_surface, self.camera)

        for item in self.reserve_items:  # <--- ADICIONE
            item.draw(self.display_surface, self.camera)

        self.hud.draw(self.display_surface)

    def reset_level(self):
        """Recomeça o nível atual"""
        from src.game.scenes.level_scene import LevelScene
        self.game.change_scene(LevelScene(self.game, level_filename=self.level_filename,
                                           return_cell=self.return_cell,
                                           node_uid=self.return_node_uid,
                                           music=self.return_music))

    def victory(self):
        # Se o nível já foi marcado como completo, retorna a cena de destino
        if self.level_complete:
            if self.return_node_uid:
                from src.game.scenes.overworld_scene import OverworldScene
                return OverworldScene(self.game, start_cell=self.return_cell)
            else:
                from src.game.scenes.title_scene import TitleScene
                return TitleScene(self.game)

        self.level_complete = True
        print("Você completou o nível!")

        if self.return_node_uid:
            try:
                node_index = self.game.overworld_node_order.index(self.return_node_uid)
                if node_index == self.game.overworld_progress:
                    self.game.overworld_progress += 1
                    print(f"[DEBUG] Progresso avançou para {self.game.overworld_progress}")
            except ValueError:
                print(f"Erro: UID {self.return_node_uid} não está na ordem.")

            from src.game.scenes.overworld_scene import OverworldScene
            return OverworldScene(self.game, start_cell=self.return_cell)
        else:
            from src.game.scenes.title_scene import TitleScene
            return TitleScene(self.game)

        return None

    def update(self):
        # print(f"[DEBUG] Item caindo em ({self.rect.x}, {self.rect.y})")
        player = self.player.sprite

        # ESTADO DE MORTE (Física da morte independente)
        if self.death_triggered:
            self.death_timer += 1

            if self.death_timer == DEATH_FREEZE_DELAY:
                player.direction.y = DEATH_JUMP_FORCE

            if self.death_timer > DEATH_FREEZE_DELAY:
                player.apply_gravity()
                player.rect.y += player.direction.y
                player.update_hitbox()

            player.animate()

            if self.death_timer >= DEATH_FREEZE_DELAY + DEATH_FADE_DELAY:
                self.death_complete = True
            return

        # 1. VERIFICAÇÃO DE QUEDA
        death_threshold = self.world_origin.y + self.level_h + DEATH_Y_THRESHOLD_OFFSET
        if player.rect.top > death_threshold:
            self.death_triggered = True
            player.die()
            return

        # 2. VERIFICAÇÃO DE VITÓRIA
        if self.goal_sprite and not self.goal_sprite.caught:
            if player.rect.colliderect(self.goal_sprite.hitbox):
                self.goal_sprite.catch()
                self.victory_triggered = True
                return

        player.get_input()
        player.get_status()
        player.animate()

        prev_rect = player.rect.copy()
        prev_hitbox = player.hitbox.copy()

        # ==========================================
        # 1. MOVE AS PLATAFORMAS (e o jogador junto)
        # ==========================================
        for platform in self.platforms:
            platform.update(self.collision_tiles)
            platform.carry_player(player)
        # ==========================================

        # ==========================================
        # 2. FÍSICA DO JOGADOR (usando o deslocamento da plataforma)
        # ==========================================
        self.physics.horizontal_collision(player, self.collision_tiles, self.blocks)
        self.physics.vertical_collision(player, prev_rect, self.collision_tiles, self.blocks, self.platforms)
        # ==========================================

        self.collect_coins()
        self.camera.update(player)

        for enemy in self.enemies:
            enemy.update(player, prev_rect, prev_hitbox)

        for mushroom in self.mushrooms:
            mushroom.update(self.collision_tiles, self.blocks, player, self)

        for fireball in self.fireballs:
            fireball.update(player)

        self.collectables.update()
        self.blocks.update()
        self.effects.update()
        self.hud.update()
        self.debris.update()

        for item in self.reserve_items:  # <--- ADICIONE
            item.update(player)

        # 3. ATUALIZA A GOALBAR MANUALMENTE
        if self.goal_sprite and not self.goal_sprite.caught:
            self.goal_sprite.update()