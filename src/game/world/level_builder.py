import pygame
from src.game.settings import *
from src.game.world.tile import Tile, SlopeTile, Decoration
from src.game.entities import Player
from src.game.world.coin import Coin
from src.game.world.mystery_box import MysteryBox
from src.game.world.yellow_box import YellowBox
from src.game.world.goal_bar import GoalBar
from src.game.entities.enemies.jumping_piranha import JumpingPiranha
from src.game.entities.enemies.volcano_lotus import VolcanoLotus
from src.game.entities.enemies.muncher import Muncher
from src.game.world.yoshi_coin import YoshiCoin
from src.game.world.moving_platform import HorizontalPlatform, VerticalPlatform
from src.game.world.rotating_block import RotatingBlock
from src.game.entities.enemies.rex import Rex
from src.game.entities.enemies.koopa import Koopa


class LevelBuilder:
    def __init__(self, game, level_data, world_origin, assets, character, level):
        self.game = game
        self.level_data = level_data
        self.world_origin = world_origin
        self.assets = assets
        self.character = character
        self.level = level

    def build(self):
        # --- Grupos locais (NÃO usar self.) ---
        tiles = pygame.sprite.Group()
        back_tiles = pygame.sprite.Group()
        front_tiles = pygame.sprite.Group()
        collision_tiles = pygame.sprite.Group()
        blocks = pygame.sprite.Group()
        mushrooms = pygame.sprite.Group()
        collectables = pygame.sprite.Group()
        player_group = pygame.sprite.GroupSingle()
        enemies = pygame.sprite.Group()
        fireballs = pygame.sprite.Group()
        platforms = pygame.sprite.Group()
        debris = pygame.sprite.Group()
        back_decoration_tiles = pygame.sprite.Group()
        front_decoration_tiles = pygame.sprite.Group()
        reserve_items = pygame.sprite.Group()

        goal_sprite = None

        wall_coords = {}
        block_coords = {}
        slope_ur = self.level_data["layers"].get("is_slope_up_right", {})
        slope_ul = self.level_data["layers"].get("is_slope_up_left", {})
        slope_dr = self.level_data["layers"].get("is_slope_down_right", {})
        slope_dl = self.level_data["layers"].get("is_slope_down_left", {})

        if "is_wall" in self.level_data["layers"]:
            wall_coords = {coord: True for coord in self.level_data["layers"]["is_wall"]}
        if "is_block" in self.level_data["layers"]:
            block_coords = {coord: True for coord in self.level_data["layers"]["is_block"]}

        if "terrain" in self.level_data["layers"]:
            for coord_str, tile_id in self.level_data["layers"]["terrain"].items():
                col, row = map(int, coord_str.split(','))
                x = (col * TILE_SIZE + self.world_origin.x)
                y = (row * TILE_SIZE + self.world_origin.y)
                image = self.assets.get_tile_image(tile_id)
                if image is None:
                    continue

                is_collidable = False
                slope_dir = None
                friction_mod = 1.0

                if coord_str in slope_ur:
                    slope_dir, friction_mod = "up_right", 1.5
                elif coord_str in slope_ul:
                    slope_dir, friction_mod = "up_left", 1.5
                elif coord_str in slope_dr:
                    slope_dir, friction_mod = "down_right", 0.55
                elif coord_str in slope_dl:
                    slope_dir, friction_mod = "down_left", 0.55

                if slope_dir is not None:
                    new_tile = SlopeTile((x, y), image, slope_dir, friction_mod)
                    is_collidable = True
                else:
                    new_tile = Tile((x, y), image)

                if coord_str in block_coords:
                    new_tile.is_block = True
                    is_collidable = True
                if coord_str in wall_coords:
                    new_tile.is_wall = True
                    is_collidable = True

                if tile_id.startswith("static_objects_tileset_6") or tile_id.startswith("static_objects_tileset_5"):
                    back_tiles.add(new_tile)
                elif tile_id.startswith("static_objects_tileset_4") or tile_id.startswith("static_objects_tileset_3"):
                    front_tiles.add(new_tile)
                else:
                    tiles.add(new_tile)

                if is_collidable:
                    collision_tiles.add(new_tile)

        if "decorations" in self.level_data["layers"]:
            for coord_str, decor_data in self.level_data["layers"]["decorations"].items():
                col, row = map(int, coord_str.split(','))
                x = (col * TILE_SIZE + self.world_origin.x)
                y = (row * TILE_SIZE + self.world_origin.y)

                # Suporta formato antigo (string) e novo (dict com "id" e "layer")
                if isinstance(decor_data, dict):
                    tile_id = decor_data.get("id", "")
                    layer = decor_data.get("layer", "back")
                else:
                    tile_id = decor_data
                    layer = "back"

                image = self.assets.get_decoration_image(tile_id)
                if image is None:
                    continue

                decoration = Decoration((x, y), image, layer)
                if layer == "front":
                    front_decoration_tiles.add(decoration)
                else:
                    back_decoration_tiles.add(decoration)

        if "spawns" in self.level_data["layers"]:
            for spawn_type, coords in self.level_data["layers"]["spawns"].items():
                for coord_str in coords:
                    col, row = map(int, coord_str.split(','))
                    x = (col * TILE_SIZE + self.world_origin.x)
                    y = (row * TILE_SIZE + self.world_origin.y)

                    if spawn_type == "Player":
                        new_player = Player((x, y), self.character, self.game)
                        new_player.level = self.level
                        player_group.add(new_player)

                    elif spawn_type == "Coin":
                        collectables.add(Coin((x, y - 4), self.assets.get_coin_frames(), self.game))

                    elif spawn_type == "MysteryBox1":
                        blocks.add(MysteryBox((x, y), self.assets.get_mystery_frames(),
                                              self.assets.get_used_block_image(), max_hits=1))

                    elif spawn_type == "MysteryBox10":
                        blocks.add(MysteryBox((x, y), self.assets.get_mystery_frames(),
                                              self.assets.get_used_block_image(), max_hits=10))

                    elif spawn_type == "YellowBox":
                        blocks.add(YellowBox((x, y), self.assets.get_yellow_frames(),
                                             self.assets.get_used_block_image(),
                                             self.assets.get_mushroom_image()))

                    elif spawn_type == "GoalBar":
                        goal_sprite = GoalBar((x, y), self.level)

                    elif spawn_type == "JumpingPiranha":
                        enemies.add(JumpingPiranha((x - 16, y), self.assets.get_piranha_frames(), self.game))

                    elif spawn_type == "VolcanoLotus":
                        lotus = VolcanoLotus((x, y), self.assets.get_volcano_plant_frames(),
                                             self.assets.get_volcano_fireball_frames(), self.game)
                        lotus.level = self.level
                        enemies.add(lotus)

                    elif spawn_type == "Muncher":
                        enemies.add(Muncher((x, y), self.assets.get_muncher_frames(), self.game))

                    elif spawn_type == "YoshiCoin":
                        collectables.add(YoshiCoin((x, y), self.assets.get_yoshi_coin_frames(), self.game))

                    elif spawn_type == "PlatformH":
                        # Pega o valor real da coordenada (True ou dict)
                        platform_data = coords[coord_str]
                        if isinstance(platform_data, dict):
                            phase = platform_data.get("phase", 0.0)
                            start_dir = platform_data.get("direction", 1)
                        else:
                            phase = 0.0
                            start_dir = 1
                        platforms.add(HorizontalPlatform((x, y), self.assets.get_horizontal_platform_surface(),
                            speed=2, range=200, phase=phase, start_direction=start_dir))

                    elif spawn_type == "PlatformV":
                        platform_data = coords[coord_str]  # True ou dict
                        if isinstance(platform_data, dict):
                            phase = platform_data.get("phase", 0.0)
                            start_dir = platform_data.get("direction", 1)
                        else:
                            phase = 0.0
                            start_dir = 1

                        platforms.add(VerticalPlatform((x, y),self.assets.get_vertical_platform_surface(),
                            speed=2, range=200, phase=phase, start_direction=start_dir))

                    elif spawn_type == "RotatingBlock":
                        block = RotatingBlock((x, y),
                                              self.assets.get_rotating_block_frames(),
                                              self.assets.get_rotating_debris_frames())
                        block.level = self.level  # Para acessar o grupo de destroços
                        blocks.add(block)

                    elif spawn_type == "Rex":
                        rex = Rex((x, y),
                                  self.assets.get_rex_big_frames(),
                                  self.assets.get_rex_small_frames(),
                                  self.assets.get_rex_dead_frame(),
                                  self.game)
                        enemies.add(rex)

                    elif spawn_type == "KoopaRed":
                        # Vermelho: vira nas bordas (patrulha), velocidade normal.
                        # Outras cores no futuro: mesma classe Koopa, só
                        # trocando os frames e esses parâmetros — ver
                        # koopa.py e a conversa sobre o comportamento das
                        # cores (verde/amarelo turns_at_edges=False,
                        # azul+amarelo speed maior, azul kicks_shells=True
                        # e hurts_on_unshelled_touch=True).
                        koopa = Koopa((x, y),
                                      self.assets.get_koopa_red_frames(),
                                      self.game,
                                      turns_at_edges=True,
                                      speed=1.0)
                        enemies.add(koopa)

        return {
            "tiles": tiles,
            "back_tiles": back_tiles,
            "front_tiles": front_tiles,
            "collision_tiles": collision_tiles,
            "blocks": blocks,
            "mushrooms": mushrooms,
            "collectables": collectables,
            "player_group": player_group,
            "enemies": enemies,
            "fireballs": fireballs,
            "goal_sprite": goal_sprite,
            "platforms": platforms,
            "back_decoration_tiles": back_decoration_tiles,
            "front_decoration_tiles": front_decoration_tiles,
            "debris": debris,
            "reserve_items": reserve_items,
        }