import os
import pygame
from src.game.graphics.spritesheet import SpriteSheet
from src.game.settings import TILES_EXPORT_DIR


class AssetManager:
    def __init__(self):
        # -----------------------------
        # SPRITESHEETS DO JOGO
        # -----------------------------
        self.animated_sheet = SpriteSheet(
            "assets/graphics/animations/animated_objects_tileset.png", 16, 16)
        self.animated_sheet_01 = SpriteSheet(
            "assets/graphics/animations/animated_objects_tileset_01.png", 16, 16)
        self.static_sheet = SpriteSheet(
            "assets/graphics/tilesets/static_objects_tileset.png", 16, 16)
        self.piranha_sheet = SpriteSheet(
            "assets/graphics/enemies/jumping_piranha.png", 16, 24)
        self.volcano_lotus_sheet = SpriteSheet(
            "assets/graphics/enemies/volcano_lotus.png", 16, 16)
        self.muncher_sheet = SpriteSheet(
            "assets/graphics/enemies/muncher.png", 16, 16)
        # Plataforma Flutuante Horizontal (tiles da linha 3, colunas 0-4)
        self.platform_sheet = SpriteSheet(
            "assets/graphics/animations/platforms_floating.png", 16, 16)
        self.rotating_block_sheet = SpriteSheet(
            "assets/graphics/animations/rotating_blocks.png", 16, 16)
        self.rotating_debris_sheet = SpriteSheet(
            "assets/graphics/animations/rotating_block_debris.png", 8, 8)
        self.rex_sheet = SpriteSheet("assets/graphics/enemies/rex.png", 16, 16)
        self.koopa_red_sheet = SpriteSheet("assets/graphics/enemies/koopa_red.png", 16, 16)

        self.horizontal_platform_surface = self._build_horizontal_platform()
        self.vertical_platform_surface = self.horizontal_platform_surface

        # -----------------------------
        # BACKGROUND
        # -----------------------------
        self.background_sheet = SpriteSheet("assets/graphics/backgrounds/backgrounds_1.png")
        self.background_image = self.background_sheet.extract_sprite(
            row=0,
            col=2,
            sprite_width=512,
            sprite_height=432,
            margin_left=8,
            margin_top=20,
            spacing_x=2,
            spacing_y=8
        )

        # -----------------------------
        # FRAMES PRÉ-CALCULADOS
        # -----------------------------
        self.coin_frames = [
            self.animated_sheet.extract_tile(row=0, col=col, scale=2)
            for col in range(3, 7)
        ]

        self.mystery_frames = [
            self.animated_sheet.extract_tile(row=2, col=col, scale=2)
            for col in range(3, 6)
        ]

        self.used_block_image = self.animated_sheet.extract_tile(row=7, col=0, scale=2)

        self.yellow_frames = [self.static_sheet.extract_tile(row=0, col=2, scale=2)]

        self.mushroom_image = self.animated_sheet_01.extract_tile(row=1, col=0, scale=2)

        self.piranha_frames = [
            self.piranha_sheet.extract_tile(row=row, col=col, scale=2)
            for row, col in [(0, 0), (0, 1), (1, 0), (1, 1)]
        ]

        # Flor completa: ocupa 2 colunas (16+16=32px, escala 2 => 64x32)
        self.volcano_plant_frames = []
        for row in range(4):
            left_tile = self.volcano_lotus_sheet.extract_tile(row=row, col=0, scale=2)
            right_tile = self.volcano_lotus_sheet.extract_tile(row=row, col=1, scale=2)
            full_flower = pygame.Surface((64, 32), pygame.SRCALPHA)
            full_flower.blit(left_tile, (0, 0))
            full_flower.blit(right_tile, (32, 0))
            self.volcano_plant_frames.append(full_flower)

        # Fireball: coluna 2 (terceira coluna), linhas 0 e 1
        self.volcano_fireball_frames = [
            self.volcano_lotus_sheet.extract_tile(row=row, col=2, scale=2)
            for row in range(2)
        ]

        self.muncher_frames = [
            self.muncher_sheet.extract_tile(row=0, col=col, scale=2)
            for col in range(2)
        ]
        # Yoshi Coin: frames com 2 tiles empilhados (linhas 5 e 6), colunas 0-4
        self.yoshi_coin_frames = []
        for col in range(5):
            top_tile = self.animated_sheet.extract_tile(row=5, col=col, scale=2)
            bottom_tile = self.animated_sheet.extract_tile(row=6, col=col, scale=2)
            # Cria uma superfície 32x64 (2 tiles com escala 2)
            full_coin = pygame.Surface((32, 64), pygame.SRCALPHA)
            full_coin.blit(top_tile, (0, 0))
            full_coin.blit(bottom_tile, (0, 32))
            self.yoshi_coin_frames.append(full_coin)

        self.rotating_block_frames = [
            self.rotating_block_sheet.extract_tile(row=0, col=col, scale=2)
            for col in range(4)
        ]
        self.rotating_debris_frames = [
            self.rotating_debris_sheet.extract_tile(row=0, col=col, scale=2)
            for col in range(6)
        ]

        # Frames grandes (cabeça + corpo) - superfície de 40x64
        self.rex_big_frames = []
        for frame_idx in range(2):
            head_tile = self.rex_sheet.extract_tile(row=0, col=frame_idx, scale=2)  # 32x32
            body_tile = self.rex_sheet.extract_tile(row=1, col=frame_idx, scale=2)  # 32x32

            rex_full = pygame.Surface((40, 64), pygame.SRCALPHA)

            # Posições base do frame 1
            head_x = 0
            head_y = 0
            body_x = 8
            body_y = 32

            # Ajustes para o frame 2
            if frame_idx == 1:
                # Cabeça desce 1px (na imagem final)
                head_y = 1
                # Corpo sobe 1px (mantendo a proporção visual)
                body_y = 31

            # Coloca o corpo (sempre 8px para a direita)
            rex_full.blit(body_tile, (body_x, body_y))
            # Coloca a cabeça (à frente, na esquerda)
            rex_full.blit(head_tile, (head_x, head_y))

            self.rex_big_frames.append(rex_full)

            # Frames pequenos (16x16 simples)
            tile_small_1 = self.rex_sheet.extract_tile(row=1, col=2, scale=2)  # 32x32
            tile_small_2 = self.rex_sheet.extract_tile(row=1, col=3, scale=2)  # 32x32 (mas conteúdo é 1px menor)

            # ==========================================================
            # CORREÇÃO: Força o frame 2 a ter EXATAMENTE 32px de altura
            # Preenchemos o espaço vazio (inferior) com transparência
            # ==========================================================
            self.rex_small_frames = []

            # Frame 1 (tamanho normal)
            self.rex_small_frames.append(tile_small_1)

            # Frame 2 (conteúdo tem 1px a menos de altura)
            # Criamos uma superfície nova de 32x32 e copiamos o conteúdo
            # deslocado 1 pixel para cima, deixando o fundo vazio embaixo.
            corrected_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Obtém a área visível real
            bounding = tile_small_2.get_bounding_rect()
            # Copia apenas o conteúdo visível para a superfície 32x32,
            # deslocando para cima (y = -1) para preencher o topo.
            corrected_surface.blit(tile_small_2, (0, -1), bounding)

            self.rex_small_frames.append(corrected_surface)

        # Frame morto (esmagado)
        self.rex_dead_frame = self.rex_sheet.extract_tile(row=1, col=4, scale=2)

        # -----------------------------
        # KOOPA VERMELHO
        # -----------------------------
        # Frames de andar (2 tiles empilhados: linha 6 = cabeça, linha 7 = pés)
        self.koopa_red_walk_frames = []
        for col in range(2):
            top_tile = self.koopa_red_sheet.extract_tile(row=6, col=col, scale=2)  # 32x32
            bottom_tile = self.koopa_red_sheet.extract_tile(row=7, col=col, scale=2)  # 32x32

            # Monta a superfície única de 32x64
            full_koopa = pygame.Surface((32, 64), pygame.SRCALPHA)
            full_koopa.blit(top_tile, (0, 0))
            full_koopa.blit(bottom_tile, (0, 32))

            self.koopa_red_walk_frames.append(full_koopa)

        # Casco parado (linha 0, coluna 5)
        self.koopa_red_shell_idle_frame = self.koopa_red_sheet.extract_tile(row=0, col=5, scale=2)

        # Casco deslizando (linha 3, colunas 3, 4, 5, 6)
        self.koopa_red_shell_slide_frames = [
            self.koopa_red_sheet.extract_tile(row=3, col=col, scale=2)
            for col in range(3, 7)
        ]

        # Sem casco andando (linha 4, colunas 6 e 7)
        self.koopa_red_unshelled_frames = [
            self.koopa_red_sheet.extract_tile(row=4, col=col, scale=2)
            for col in range(6, 8)
        ]

        # Frame de "sendo expelido do casco" (linha 6, colunas 3, 6, 7)
        # Este frame será usado futuramente no estado "pop_out"
        self.koopa_red_pop_out_frames = [
            self.koopa_red_sheet.extract_tile(row=6, col=col, scale=2)
            for col in [6, 7]
        ]
        self.koopa_red_squashed_frame = self.koopa_red_sheet.extract_tile(row=5, col=5, scale=2)

        # Koopa alado (Paratroopa): cada pose ocupa um bloco 2x2 de tiles
        # (2 colunas de largura x 2 linhas de altura — linha 8 = cabeça,
        # linha 9 = corpo, igual ao walk_frames, só que também precisa de
        # 2 colunas porque a asa estende a silhueta pros lados).
        def build_wing_pose(col_left, col_right):
            top_left = self.koopa_red_sheet.extract_tile(row=8, col=col_left, scale=2)
            top_right = self.koopa_red_sheet.extract_tile(row=8, col=col_right, scale=2)
            bottom_left = self.koopa_red_sheet.extract_tile(row=9, col=col_left, scale=2)
            bottom_right = self.koopa_red_sheet.extract_tile(row=9, col=col_right, scale=2)

            pose = pygame.Surface((64, 64), pygame.SRCALPHA)
            pose.blit(top_left, (0, 0))
            pose.blit(top_right, (32, 0))
            pose.blit(bottom_left, (0, 32))
            pose.blit(bottom_right, (32, 32))
            return pose

        self.koopa_red_fly_frames = [
            build_wing_pose(2, 3),
            build_wing_pose(4, 5),
        ]
        self.koopa_red_fly_turn_frame = build_wing_pose(6, 7)

        # -----------------------------
        # CACHE DE TILES (carregados dinamicamente do disco)
        # -----------------------------
        self.tile_image_cache = {}

    def load_tile_images(self):
        """Escaneia a pasta tiles_export e carrega todas as imagens na memória."""
        if not os.path.exists(TILES_EXPORT_DIR):
            print(f"ERRO: Pasta de tiles não encontrada em {TILES_EXPORT_DIR}")
            return

        for filename in os.listdir(TILES_EXPORT_DIR):
            if filename.endswith(".png"):
                tile_id = filename.replace(".png", "")
                filepath = os.path.join(TILES_EXPORT_DIR, filename)

                try:
                    image = pygame.image.load(filepath).convert()
                    image.set_colorkey((255, 0, 255))  # Torna o magenta transparente
                    self.tile_image_cache[tile_id] = image
                except pygame.error:
                    print(f"Erro ao carregar imagem: {filename}")

    def get_tile_image(self, tile_id):
        """Retorna a imagem do tile do cache, ou None se não existir."""
        return self.tile_image_cache.get(tile_id)

    def _build_horizontal_platform(self):
        """Monta a plataforma horizontal juntando 5 tiles em uma superfície única."""
        # Extrai os 5 tiles (escala 2 = 32x32 cada)
        tiles = [self.platform_sheet.extract_tile(row=3, col=col, scale=2) for col in range(5)]

        # Cria uma superfície única de 160x32 pixels
        platform_surface = pygame.Surface((160, 32), pygame.SRCALPHA)
        for i, tile in enumerate(tiles):
            platform_surface.blit(tile, (i * 32, 0))

        return platform_surface


    # -----------------------------
    # MÉTODOS PÚBLICOS (para o Level)
    # -----------------------------
    def get_background_image(self):
        return self.background_image

    def get_coin_frames(self):
        return self.coin_frames

    def get_mystery_frames(self):
        return self.mystery_frames

    def get_used_block_image(self):
        return self.used_block_image

    def get_yellow_frames(self):
        return self.yellow_frames

    def get_mushroom_image(self):
        return self.mushroom_image

    def get_piranha_frames(self):
        return self.piranha_frames

    def get_volcano_plant_frames(self):
        return self.volcano_plant_frames

    def get_volcano_fireball_frames(self):
        return self.volcano_fireball_frames

    def get_muncher_frames(self):
        return self.muncher_frames

    def get_yoshi_coin_frames(self):
        return self.yoshi_coin_frames

    def get_horizontal_platform_surface(self):
        return self.horizontal_platform_surface

    def get_vertical_platform_surface(self):
        return self.vertical_platform_surface

    def get_decoration_image(self, decoration_id):
        """Retorna a imagem de um tile de decoração do cache."""
        return self.tile_image_cache.get(decoration_id)

    def get_rotating_block_frames(self):
        return self.rotating_block_frames

    def get_rotating_debris_frames(self):
        return self.rotating_debris_frames

    def get_rex_big_frames(self):
        return self.rex_big_frames

    def get_rex_small_frames(self):
        return self.rex_small_frames

    def get_rex_dead_frame(self):
        return self.rex_dead_frame

    def get_koopa_red_frames(self):
        return {
            "walk": self.koopa_red_walk_frames,
            "shell_idle": self.koopa_red_shell_idle_frame,
            "shell_slide": self.koopa_red_shell_slide_frames,
            "unshelled": self.koopa_red_unshelled_frames,
            "pop_out": self.koopa_red_pop_out_frames,
            "squashed": self.koopa_red_squashed_frame,
        }