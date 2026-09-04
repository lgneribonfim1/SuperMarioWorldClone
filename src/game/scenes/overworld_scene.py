import os
import json
import pygame
from collections import deque  # <--- ADICIONADO
from src.game.scenes.scene import Scene
from src.game.settings import (
    TILE_SIZE, LEVELS_DIR, OVERWORLD_EXPORT_DIR,
    INTERNAL_WIDTH, INTERNAL_HEIGHT,
)
from src.game.entities.overworld_player import OverworldPlayer


class OverworldScene(Scene):
    """Tela de mapa-múndi com movimento restrito a caminhos e progresso sequencial."""

    def __init__(self, game, overworld_filename="overworld_1.json", start_cell=None):
        super().__init__(game)
        self.game.audio.play_music("yoshi_s_island")

        self.overworld_file = os.path.join(LEVELS_DIR, overworld_filename)
        self.tile_image_cache = {}
        self.terrain_layer = {}
        self.path_cells = set()
        self.nodes = {}
        self.uid_to_pos = {}
        self.spawn_cell = None
        self.message = ""
        self.message_timer = 0

        self._load_tile_images()
        self._load_overworld()

        self._setup_node_progress()

        # Cria o jogador
        start = start_cell or self.spawn_cell or (0, 0)
        avatar_frame = self._load_avatar_frame()

        # ===========================================================
        # CORREÇÃO FINAL: Caminho contínuo até o nó desbloqueado, parando após ele
        # ===========================================================
        walkable_cells = self._get_walkable_cells()

        self.player = OverworldPlayer(
            start[0], start[1],
            walkable_cells=walkable_cells,
            frame=avatar_frame
        )
        # ===========================================================

        self.level_w = self.grid_width * TILE_SIZE
        self.level_h = self.grid_height * TILE_SIZE
        self.camera_x = 0
        self.camera_y = 0
        self._update_camera(snap=True)

    # ------------------------------------------------------------
    # CARREGAMENTO
    # ------------------------------------------------------------
    def _load_tile_images(self):
        for folder_name in ('terrain', 'nodes'):
            folder_path = os.path.join(OVERWORLD_EXPORT_DIR, folder_name)
            if not os.path.exists(folder_path):
                continue
            for filename in os.listdir(folder_path):
                if not filename.endswith(".png"):
                    continue
                tile_id = filename.replace(".png", "")
                filepath = os.path.join(folder_path, filename)
                try:
                    image = pygame.image.load(filepath).convert()
                    image.set_colorkey((255, 0, 255))
                    self.tile_image_cache[tile_id] = image
                except pygame.error:
                    print(f"Erro ao carregar imagem do overworld: {filename}")

    def _load_avatar_frame(self):
        from src.game.settings import ASSETS_DIR
        path = os.path.join(ASSETS_DIR, "graphics", "overworld", "sprites", "overworld_spritesheet.png")
        row, col = (0, 0) if self.game.selected_character == "mario" else (0, 6)
        SPRITE_SIZE = 16
        try:
            sheet = pygame.image.load(path).convert()
            sheet.set_colorkey((255, 0, 255))
            src_rect = pygame.Rect(col * SPRITE_SIZE, row * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE)
            frame = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), src_rect)
            return pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE))
        except (pygame.error, FileNotFoundError):
            frame = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(frame, (220, 30, 30), frame.get_rect())
            return frame

    def _load_overworld(self):
        try:
            with open(self.overworld_file, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"ERRO ao carregar overworld '{self.overworld_file}': {e}")
            data = {"width": 20, "height": 15, "layers": {"terrain": {}, "paths": {}, "nodes": {}}}

        self.grid_width = data.get("width", 20)
        self.grid_height = data.get("height", 15)
        layers = data.get("layers", {})

        for coord_str, tile_id in layers.get("terrain", {}).items():
            col, row = map(int, coord_str.split(','))
            self.terrain_layer[(col, row)] = tile_id

        for coord_str in layers.get("paths", {}):
            col, row = map(int, coord_str.split(','))
            self.path_cells.add((col, row))

        import uuid
        for coord_str, node_data in layers.get("nodes", {}).items():
            col, row = map(int, coord_str.split(','))
            if "uid" not in node_data:
                node_data["uid"] = str(uuid.uuid4())[:8]
            if "order" not in node_data:
                node_data["order"] = 999
            if "music" not in node_data:
                node_data["music"] = "overworld"

            self.nodes[(col, row)] = node_data
            self.uid_to_pos[node_data["uid"]] = (col, row)

        if self.nodes:
            first_key = next(iter(self.nodes))
            self.spawn_cell = first_key

    def _setup_node_progress(self):
        node_list = sorted(
            [(pos, data) for pos, data in self.nodes.items() if pos != self.spawn_cell],
            key=lambda kv: kv[1].get("order", 999)
        )

        self.game.overworld_node_order = [data["uid"] for _, data in node_list]

        if self.game.overworld_progress >= len(self.game.overworld_node_order):
            self.game.overworld_progress = len(self.game.overworld_node_order) - 1

    # ===========================================================
    # CORREÇÃO DA ÁREA DE BLOQUEIO (Caminho contínuo até o nó, parada 1 tile após)
    # ===========================================================
    def _find_path(self, start, target):
        """Encontra uma sequência de células de caminho que liga start até target."""
        if start == target:
            return [start]

        queue = deque([(start, [start])])
        visited = set()
        visited.add(start)

        while queue:
            current, path = queue.popleft()
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in visited:
                    continue
                if neighbor in self.path_cells or neighbor == target:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    if neighbor == target:
                        return new_path
                    queue.append((neighbor, new_path))
        return []

    # ===========================================================
    # CORREÇÃO FINAL: Libera o caminho inteiro e os vizinhos de TODOS os nós desbloqueados
    # ===========================================================
    # ===========================================================
    # CORREÇÃO FINAL: BFS agora pisa em Nós desbloqueados e libera vizinhos de todos
    # ===========================================================
    def _get_walkable_cells(self):
        walkable = set()

        # 1. Sempre libera o Spawn
        walkable.add(self.spawn_cell)

        # 2. Pega todos os nós desbloqueados (do índice 0 até o progresso atual)
        unlocked_nodes = set()
        for i, uid in enumerate(self.game.overworld_node_order):
            if i <= self.game.overworld_progress and uid in self.uid_to_pos:
                unlocked_nodes.add(self.uid_to_pos[uid])

        if not unlocked_nodes:
            return walkable

        # 3. Encontra o último nó desbloqueado (o destino da BFS)
        last_unlocked_uid = self.game.overworld_node_order[self.game.overworld_progress]
        last_unlocked_pos = self.uid_to_pos.get(last_unlocked_uid)

        if last_unlocked_pos:
            # 4. BFS que permite andar tanto em 'path_cells' QUANTO em 'unlocked_nodes'
            from collections import deque
            queue = deque([(self.spawn_cell, [self.spawn_cell])])
            visited = set()
            visited.add(self.spawn_cell)

            found_path = []
            while queue:
                current, path = queue.popleft()
                if current == last_unlocked_pos:
                    found_path = path
                    break
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    neighbor = (current[0] + dx, current[1] + dy)
                    if neighbor in visited:
                        continue
                    # A NOVA CONDIÇÃO: pode pisar em caminhos OU em nós desbloqueados
                    if neighbor in self.path_cells or neighbor in unlocked_nodes:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))

            # 5. Adiciona o caminho encontrado pela BFS
            if found_path:
                walkable.update(found_path)

            # 6. Adiciona todos os nós desbloqueados.
            #    Só libera os vizinhos se NÃO for o último nó (para parar exatamente nele).
            for node_pos in unlocked_nodes:
                walkable.add(node_pos)
                # Se este não for o último nó desbloqueado, ele pode sair dele e andar pelos vizinhos
                if node_pos != last_unlocked_pos:
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        neighbor = (node_pos[0] + dx, node_pos[1] + dy)
                        if neighbor in self.path_cells:
                            walkable.add(neighbor)

        return walkable

    # ===========================================================

    # ------------------------------------------------------------
    # CÂMERA
    # ------------------------------------------------------------
    def _update_camera(self, snap=False):
        target_x = self.player.pixel_pos.x - INTERNAL_WIDTH // 2
        target_y = self.player.pixel_pos.y - INTERNAL_HEIGHT // 2
        if snap:
            self.camera_x, self.camera_y = target_x, target_y
        else:
            self.camera_x += (target_x - self.camera_x) * 0.15
            self.camera_y += (target_y - self.camera_y) * 0.15
        max_x = max(0, self.level_w - INTERNAL_WIDTH)
        max_y = max(0, self.level_h - INTERNAL_HEIGHT)
        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))

    def apply(self, rect):
        return rect.move(-int(self.camera_x), -int(self.camera_y))

    # ------------------------------------------------------------
    # LÓGICA DE ENTRADA NO NÓ
    # ------------------------------------------------------------
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._try_enter_node()

    def _try_enter_node(self):
        if self.player.moving:
            return

        cell = self.player.current_cell
        if cell == self.spawn_cell:
            return

        node_data = self.nodes.get(cell)
        if node_data is None:
            return

        node_uid = node_data.get("uid")
        level_file = node_data.get("level_file", "placeholder.json")

        if level_file == "placeholder.json":
            self.message = "Essa fase ainda não foi criada!"
            self.message_timer = 90
            return

        try:
            node_index = self.game.overworld_node_order.index(node_uid)
        except ValueError:
            self.message = "Nó não registrado na ordem!"
            self.message_timer = 90
            return

        if node_index > self.game.overworld_progress:
            self.message = "Nível bloqueado!"
            self.message_timer = 90
            return

        from src.game.scenes.level_scene import LevelScene
        self.game.change_scene(
            LevelScene(
                self.game,
                level_filename=level_file,
                return_cell=cell,
                node_uid=node_uid,
                music=node_data.get("music", "overworld")
            )
        )

    # ------------------------------------------------------------
    # DESENHO DOS NÓS
    # ------------------------------------------------------------
    def _draw_node_tiles(self, surface, col, row, node_data):
        node_type = node_data.get("type", "Level")
        mapping = {
            "Level": [(0, 0, "node_2_3")],
            "Cave": [(0, 0, "node_3_1")],
            "GhostHouse": [(0, 0, "node_2_4")],
            "CastleSmall": [(0, 0, "node_2_9")],
            "CastleMedium": [(0, 0, "node_1_9"), (0, -1, "node_0_9")],
            "CastleLarge": [
                (-1, 0, "node_4_2"), (0, 0, "node_4_3"), (1, 0, "node_4_4"),
                (-1, -1, "node_3_2"), (0, -1, "node_3_3"), (1, -1, "node_3_4")
            ],
            "CastleBoss": [(0, 0, "node_1_8"), (0, -1, "node_0_8")],
        }

        if node_type == "Spawn":
            return
        tile_list = mapping.get(node_type, mapping["Level"])
        for dcol, drow, tile_id in tile_list:
            image = self.tile_image_cache.get(tile_id)
            if image is None:
                continue
            draw_col = col + dcol
            draw_row = row + drow
            rect = pygame.Rect(draw_col * TILE_SIZE, draw_row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            surface.blit(image, self.apply(rect))

    # ------------------------------------------------------------
    # DESENHO PRINCIPAL
    # ------------------------------------------------------------
    def draw(self):
        surface = self.game.surface
        surface.fill((92, 148, 252))

        for (col, row), tile_id in self.terrain_layer.items():
            image = self.tile_image_cache.get(tile_id)
            if image is None:
                continue
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            surface.blit(image, self.apply(rect))

        for (col, row), node_data in self.nodes.items():
            self._draw_node_tiles(surface, col, row, node_data)

        self.player.draw(surface, self)

        if (not self.player.moving and
                self.player.current_cell in self.nodes and
                self.player.current_cell != self.spawn_cell):
            font = pygame.font.Font(None, 24)
            hint = font.render("Pressione ENTER para jogar", True, "white")
            hint_rect = hint.get_rect(center=(INTERNAL_WIDTH // 2, INTERNAL_HEIGHT - 24))
            bg = pygame.Surface((hint_rect.width + 16, hint_rect.height + 8))
            bg.set_alpha(160)
            bg.fill((0, 0, 0))
            surface.blit(bg, (hint_rect.x - 8, hint_rect.y - 4))
            surface.blit(hint, hint_rect)

        if self.message:
            font = pygame.font.Font(None, 28)
            text = font.render(self.message, True, "yellow")
            text_rect = text.get_rect(center=(INTERNAL_WIDTH // 2, 40))
            surface.blit(text, text_rect)

    def update(self):
        self.player.update()
        self._update_camera()
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""

"""
mapping = {
            "Level": [(0, 0, "node_2_3")],
            "Cave": [(0, 0, "node_3_1")],
            "GhostHouse": [(0, 0, "node_2_4")],
            "CastleSmall": [(0, 0, "node_2_9")],
            "CastleMedium": [(0, 0, "node_1_9"), (0, -1, "node_0_9")],
            "CastleLarge": [
                (-1, 0, "node_4_2"), (0, 0, "node_4_3"), (1, 0, "node_4_4"),
                (-1, -1, "node_3_2"), (0, -1, "node_3_3"), (1, -1, "node_3_4")
            ],
            "CastleBoss": [(0, 0, "node_1_8"), (0, -1, "node_0_8")],
        }
"""