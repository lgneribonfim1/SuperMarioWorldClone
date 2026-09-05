import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import json
import os


class TileEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Super Mario World - Tile Editor")
        self.root.geometry("1100x700")
        self.root.configure(bg="#2b2b2b")

        self.TILE_SIZE = 32
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.EXPORT_DIR = os.path.join(self.BASE_DIR, 'game', 'assets', 'tiles_export')

        # Camadas de dados do mapa
        self.decoration_layer = {}
        self.tile_layer = {}
        self.wall_layer = {}
        self.block_layer = {}
        self.spawn_layer = {}

        # === NOVAS CAMADAS DE RAMPA ===
        self.slope_up_right_layer = {}
        self.slope_up_left_layer = {}
        self.slope_down_right_layer = {}
        self.slope_down_left_layer = {}

        # Mapa ferramenta -> camada correspondente, pra _paint_cell não
        # precisar de um if/elif repetido pra cada uma (wall/block/rampas
        # seguem exatamente a mesma lógica de "presença = True").
        self.TOOL_LAYERS = {
            "wall_brush": self.wall_layer,
            "block_brush": self.block_layer,
            "slope_up_right": self.slope_up_right_layer,
            "slope_up_left": self.slope_up_left_layer,
            "slope_down_right": self.slope_down_right_layer,
            "slope_down_left": self.slope_down_left_layer,
        }

        self.tile_images = {}
        self.tile_buttons = {}
        self.selected_tile_id = None

        self.grid_width = 200
        self.grid_height = 50
        self.current_tool = "brush"
        self.spawn_type = "Player"

        # Nomes das 4 ferramentas de rampa — usado pra saber quais tools
        # são "rampa" (mutuamente exclusivas entre si) sem espalhar essa
        # lista em vários lugares do código.
        self.SLOPE_TOOLS = ("slope_up_right", "slope_up_left", "slope_down_right", "slope_down_left")

        # Estado do traço de pintura atual (decidido no primeiro tile tocado
        # em cada clique/arraste — ver _paint_cell). None = nenhum traço em
        # andamento.
        self._drag_action = None

        self.setup_ui()
        self.load_tiles()
        self.draw_grid()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_frame, width=230, bg="#3c3c3c")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)

        # Topo: Ferramentas
        top_frame = tk.Frame(left_frame, bg="#3c3c3c")
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=(1, 1))
        tk.Label(top_frame, text="TOOLS", bg="#3c3c3c", fg="white", font=("Arial", 12, "bold")).pack()

        btn_frame = tk.Frame(top_frame, bg="#3c3c3c")
        btn_frame.pack(pady=1)

        # Linha 1: Pincel e Borracha
        tk.Button(btn_frame, text="BRUSH", bg="#90EE90", command=lambda: self.set_tool("brush"),
                  width=6).grid(row=0, column=0, padx=1, pady=1)

        tk.Button(btn_frame, text="ERASER", bg="#FF9999", command=lambda: self.set_tool("erase"),
                  width=6).grid(row=0, column=1, padx=1, pady=1)

        tk.Button(btn_frame, text="DECOR B", bg="#ADD8E6", command=lambda: self.set_tool("decoration_back_brush"),
                  width=7).grid(row=0, column=2, padx=1, pady=1)
        tk.Button(btn_frame, text="DECOR F", bg="#FFB6C1", command=lambda: self.set_tool("decoration_front_brush"),
                  width=7).grid(row=1, column=2, padx=1, pady=1)

        # Linha 2: Parede e Bloco
        tk.Button(btn_frame, text="WALL", bg="#FFA500", fg="white", command=lambda: self.set_tool("wall_brush"),
                  width=6).grid(row=1, column=0, padx=1, pady=1)
        tk.Button(btn_frame, text="BLOCK", bg="#4169E1", fg="white", command=lambda: self.set_tool("block_brush"),
                  width=6).grid(row=1, column=1, padx=1, pady=1)

        # Linha 3: Rampas (As 4 novas ferramentas)
        tk.Label(btn_frame, text="SLOPES (45 graus)", bg="#3c3c3c", fg="white",
                 font=("Arial", 9)).grid(row=2, column=0, columnspan=2, pady=(1, 0))

        tk.Button(btn_frame, text="⬆ Esq", bg="#ADFF2F", command=lambda: self.set_tool("slope_up_left"), width=6).grid(
            row=3, column=0, padx=1, pady=1)
        tk.Button(btn_frame, text="⬆ Dir", bg="#ADFF2F", command=lambda: self.set_tool("slope_up_right"), width=6).grid(
            row=3, column=1, padx=1, pady=1)
        tk.Button(btn_frame, text="⬇ Esq", bg="#ADFF2F", command=lambda: self.set_tool("slope_down_left"),
                  width=6).grid(row=4, column=0, padx=1, pady=1)
        tk.Button(btn_frame, text="⬇ Dir", bg="#ADFF2F", command=lambda: self.set_tool("slope_down_right"),
                  width=6).grid(row=4, column=1, padx=1, pady=1)

        # Linha 4: Spawn
        tk.Label(btn_frame, text="Tipo:", bg="#3c3c3c", fg="white",
                 font=("Arial", 9)).grid(row=5, column=0, pady=(1, 0))
        self.spawn_var = tk.StringVar(value="Player")
        spawn_combo = ttk.Combobox(btn_frame, textvariable=self.spawn_var,
                                             values=["Player", "Coin", "MysteryBox1", "MysteryBox10",
                                                     "YellowBox", "Goomba", "GoalBar", "JumpingPiranha",
                                                     "VolcanoLotus", "Muncher", "YoshiCoin", "PlatformH",
                                                     "PlatformV", "RotatingBlock", "Rex", "KoopaRed",
                                                     "ParatroopaRed"],
                                            width=12, state="readonly")
        spawn_combo.grid(row=5, column=1, pady=(1, 0))

        tk.Button(btn_frame, text="Marcador", bg="#8A2BE2", fg="white", command=lambda: self.set_tool("spawn_brush"),
                  width=10).grid(row=6, column=0, columnspan=2, pady=1)

        # Meio: Abas (NOTEBOOK)
        tile_container = tk.Frame(left_frame, bg="#3c3c3c")
        tile_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(1, 0))
        tk.Label(tile_container, text="TILES", bg="#3c3c3c", fg="white", font=("Arial", 12, "bold")).pack()

        self.notebook = ttk.Notebook(tile_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=1)

        categories = ["decor", "pipes", "block", "terra"]
        self.category_widgets = {}

        for cat in categories:
            frame = tk.Frame(self.notebook, bg="#505050")
            self.notebook.add(frame, text=cat.capitalize())

            canvas = tk.Canvas(frame, bg="#505050", highlightthickness=0)
            scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            inner_frame = tk.Frame(canvas, bg="#505050")
            canvas.create_window((0, 0), window=inner_frame, anchor="nw")

            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.category_widgets[cat] = {"frame": inner_frame, "canvas": canvas}

        # Fundo: Nível e Salvar
        bottom_frame = tk.Frame(left_frame, bg="#3c3c3c")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=2, padx=10)
        tk.Label(bottom_frame, text="NÍVEL", bg="#3c3c3c", fg="white", font=("Arial", 12, "bold")).pack()
        size_frame = tk.Frame(bottom_frame, bg="#3c3c3c")
        size_frame.pack(pady=2)

        tk.Label(size_frame, text="Width:", bg="#3c3c3c", fg="white").pack(side=tk.LEFT, padx=2)
        self.width_var = tk.IntVar(value=200)
        tk.Spinbox(size_frame, from_=10, to=1000, textvariable=self.width_var, width=5).pack(side=tk.LEFT)

        tk.Label(size_frame, text="Height:", bg="#3c3c3c", fg="white").pack(side=tk.LEFT, padx=5)
        self.height_var = tk.IntVar(value=50)
        tk.Spinbox(size_frame, from_=10, to=1000, textvariable=self.height_var, width=5).pack(side=tk.LEFT)

        self.width_var.trace_add("write", self.update_grid_size)
        self.height_var.trace_add("write", self.update_grid_size)

        load_btn = tk.Button(bottom_frame, text="LOAD MAP (.json)", bg="#4682B4", fg="white",
                             font=("Arial", 10, "bold"), command=self.load_map)
        load_btn.pack(pady=(1, 1), fill=tk.X)

        tk.Button(bottom_frame, text="SAVE MAP (.json)", bg="#228B22", fg="white",
                  font=("Arial", 10, "bold"), command=self.save_map).pack(pady=1, fill=tk.X)

        # --- LADO DIREITO (GRID) ---
        right_frame = tk.Frame(main_frame, bg="#007474")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.h_scroll = tk.Scrollbar(right_frame, orient=tk.HORIZONTAL)
        self.v_scroll = tk.Scrollbar(right_frame, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(right_frame, bg="#007474", highlightthickness=0,
                                xscrollcommand=self.h_scroll.set,
                                yscrollcommand=self.v_scroll.set)
        self.h_scroll.config(command=self.canvas.xview)
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.root.bind("<Key>", self._on_key_press)
        self.root.focus_set()

    def update_grid_size(self, *args):
        try:
            new_w = self.width_var.get()
            new_h = self.height_var.get()
            if new_w < 1: new_w = 1
            if new_h < 1: new_h = 1
            self.grid_width = new_w
            self.grid_height = new_h
            self.draw_grid()
        except tk.TclError:
            pass

    def load_tiles(self):
        if not os.path.exists(self.EXPORT_DIR):
            messagebox.showerror("Erro", f"Pasta 'tiles_export' não encontrada!")
            return

        CATEGORY_PREFIXES = {
            "decor": "decorations_trees",
            "pipes": "pipes_tileset",
            "block": "static_objects_tileset",
            "terra": "terrain_1"
        }

        categorized_files = {cat: [] for cat in CATEGORY_PREFIXES}
        for filename in os.listdir(self.EXPORT_DIR):
            if filename.endswith('.png'):
                for cat, prefix in CATEGORY_PREFIXES.items():
                    if filename.startswith(prefix):
                        categorized_files[cat].append(filename)
                        break

        for cat, files in categorized_files.items():
            widgets = self.category_widgets[cat]
            frame = widgets["frame"]
            canvas = widgets["canvas"]

            for widget in frame.winfo_children():
                widget.destroy()

            col_count = 0
            row_count = 0
            max_cols = 5

            for filename in sorted(files):
                tile_id = filename.replace('.png', '')
                filepath = os.path.join(self.EXPORT_DIR, filename)

                img = Image.open(filepath)
                photo = ImageTk.PhotoImage(img)
                self.tile_images[tile_id] = photo

                btn = tk.Button(frame, image=photo, bd=0, bg="#505050", activebackground="#FFD700",
                                command=lambda tid=tile_id: self.select_tile(tid))
                btn.grid(row=row_count, column=col_count, padx=2, pady=2)
                self.tile_buttons[tile_id] = btn

                col_count += 1
                if col_count >= max_cols:
                    col_count = 0
                    row_count += 1

            frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

    def select_tile(self, tile_id):
        for btn in self.tile_buttons.values():
            btn.config(bd=0)
        if tile_id in self.tile_buttons:
            self.tile_buttons[tile_id].config(bd=3, relief="solid", highlightbackground="#FFD700")
        self.selected_tile_id = tile_id

    def set_tool(self, tool):
        self.current_tool = tool
        self.spawn_type = self.spawn_var.get()

    def _on_key_press(self, event):
        if event.keysym == 'w':
            self.canvas.yview_scroll(-1, "units")
        elif event.keysym == 's':
            self.canvas.yview_scroll(1, "units")
        elif event.keysym == 'a':
            self.canvas.xview_scroll(-1, "units")
        elif event.keysym == 'd':
            self.canvas.xview_scroll(1, "units")

    def draw_grid(self):
        self.canvas.delete("all")
        w = self.grid_width * self.TILE_SIZE
        h = self.grid_height * self.TILE_SIZE
        self.canvas.config(scrollregion=(0, 0, w, h))

        for x in range(0, w + 1, self.TILE_SIZE):
            self.canvas.create_line(x, 0, x, h, fill="#505050", width=1)
        for y in range(0, h + 1, self.TILE_SIZE):
            self.canvas.create_line(0, y, w, y, fill="#505050", width=1)

        # Terreno
        for (col, row), tile_id in self.tile_layer.items():
            if tile_id in self.tile_images:
                x = col * self.TILE_SIZE
                y = row * self.TILE_SIZE
                self.canvas.create_image(x, y, anchor=tk.NW, image=self.tile_images[tile_id])

        # Decorações (árvores, arbustos, etc.)
        for (col, row), decor_data in self.decoration_layer.items():
            tile_id = decor_data.get("id", "") if isinstance(decor_data, dict) else decor_data
            if tile_id in self.tile_images:
                x = col * self.TILE_SIZE
                y = row * self.TILE_SIZE
                self.canvas.create_image(x, y, anchor=tk.NW, image=self.tile_images[tile_id])

        # Camada de Parede (Laranja)
        for (col, row) in self.wall_layer:
            x = col * self.TILE_SIZE
            y = row * self.TILE_SIZE
            self.canvas.create_rectangle(x, y, x + self.TILE_SIZE, y + self.TILE_SIZE,
                                         fill="#FFA500", stipple="gray50", outline="#FF8C00", width=2)

        # Camada de Bloco (Azul)
        for (col, row) in self.block_layer:
            x = col * self.TILE_SIZE
            y = row * self.TILE_SIZE
            self.canvas.create_rectangle(x, y, x + self.TILE_SIZE, y + self.TILE_SIZE,
                                         fill="#4169E1", stipple="gray50", outline="#0000CD", width=2)

        # ==========================================
        # CAMADAS DE RAMPA (Polígonos de 45 graus)
        # ==========================================
        # "up_right" e "down_left" são o MESMO triângulo fisicamente (sobe
        # da esquerda pra direita — ver SlopeTile.height_at no jogo, que
        # agrupa as duas no mesmo cálculo); "up_left" e "down_right" também
        # formam o outro par idêntico. A única diferença real entre a
        # versão "up" e a "down" é o atrito (grudenta vs escorregadia), não
        # o formato — por isso aqui elas usam o MESMO triângulo do seu par,
        # só com cor diferente (verde = grudenta, azul-gelo = escorregadia)
        # pra dar pra distinguir no editor sem inventar um formato errado.
        grip_color, grip_outline = "#ADFF2F", "#32CD32"      # verde-limão: rampa "grudenta"
        slip_color, slip_outline = "#87CEFA", "#1E90FF"      # azul-gelo: rampa "escorregadia"

        def draw_slope(col, row, direction, fill, outline):
            x, y = col * self.TILE_SIZE, row * self.TILE_SIZE
            size = self.TILE_SIZE

            if direction in ("up_right", "down_left"):
                # sobe da esquerda pra direita: sólido é o triângulo
                # inferior-direito (embaixo da diagonal bottom-left -> top-right)
                pts = [x, y + size, x + size, y, x + size, y + size]
            else:  # "up_left", "down_right"
                # sobe da direita pra esquerda: sólido é o triângulo
                # inferior-esquerdo (embaixo da diagonal top-left -> bottom-right)
                pts = [x, y, x + size, y + size, x, y + size]

            self.canvas.create_polygon(pts, fill=fill, stipple="gray50",
                                       outline=outline, width=2)

        for (col, row) in self.slope_up_right_layer:
            draw_slope(col, row, "up_right", grip_color, grip_outline)
        for (col, row) in self.slope_up_left_layer:
            draw_slope(col, row, "up_left", grip_color, grip_outline)
        for (col, row) in self.slope_down_right_layer:
            draw_slope(col, row, "down_right", slip_color, slip_outline)
        for (col, row) in self.slope_down_left_layer:
            draw_slope(col, row, "down_left", slip_color, slip_outline)
        # ==========================================

        # Camada de Spawn (Roxo)
        for (col, row), spawn_data in self.spawn_layer.items():
            x = col * self.TILE_SIZE
            y = row * self.TILE_SIZE
            self.canvas.create_rectangle(x, y, x + self.TILE_SIZE, y + self.TILE_SIZE,
                                             fill="#8A2BE2", stipple="gray50", outline="#4B0082", width=2)

            # ==========================================
            # Extrai o tipo do spawn (string ou dict)
            # ==========================================
            if isinstance(spawn_data, dict):
                spawn_type = spawn_data.get("type", "PlatformH")  # fallback
            else:
                spawn_type = spawn_data
            # ==========================================

            spawn_symbols = {
                "Player": "P", "Coin": "C", "MysteryBox1": "1",
                "MysteryBox10": "10", "YellowBox": "Y", "Goomba": "G",
                "GoalBar": "F", "JumpingPiranha": "J", "VolcanoLotus": "V",
                "Muncher": "M", "YoshiCoin": "YC", "PlatformH": "PH",
                "PlatformV": "PV", "RotatingBlock": "RB", "Rex": "RX",
                "KoopaRed": "KR", "ParatroopaRed": "PR"
            }
            symbol = spawn_symbols.get(spawn_type, spawn_type[0])
            self.canvas.create_text(x + self.TILE_SIZE // 2, y + self.TILE_SIZE // 2,
                                        text=symbol, fill="white", font=("Arial", 12, "bold"))

    def _clear_slopes(self, coord):
        """Remove `coord` das 4 camadas de rampa. Uma célula só pode ser UMA
        direção de rampa por vez — sem isso, dava pra empilhar duas rampas
        diferentes na mesma célula (o jogo só usaria a primeira que
        encontrasse ao carregar, mas o editor desenhava os dois triângulos
        sobrepostos, o que é confuso e não reflete o que vai pro jogo)."""
        for layer_name in ("slope_up_right", "slope_up_left", "slope_down_right", "slope_down_left"):
            self.TOOL_LAYERS[layer_name].pop(coord, None)

    def _paint_cell(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        col = int(x // self.TILE_SIZE)
        row = int(y // self.TILE_SIZE)

        if col >= self.grid_width or row >= self.grid_height or col < 0 or row < 0:
            return

        coord = (col, row)
        tool = self.current_tool

        if tool == "brush":
            # Sempre "seta" o valor (nunca alterna) — por isso já funcionava
            # bem arrastando: passar de novo pela mesma célula no meio de um
            # arraste não desfaz o que acabou de ser pintado.
            if self.selected_tile_id:
                self.tile_layer[coord] = self.selected_tile_id


        elif tool in ("decoration_back_brush", "decoration_front_brush"):
            if self.selected_tile_id:
                layer = "back" if tool == "decoration_back_brush" else "front"
                self.decoration_layer[coord] = {"id": self.selected_tile_id, "layer": layer}


        elif tool == "erase":
            for layer in (self.tile_layer, self.wall_layer, self.block_layer,
                          self.slope_up_right_layer, self.slope_up_left_layer,
                          self.slope_down_right_layer, self.slope_down_left_layer,
                          self.decoration_layer,
                          self.spawn_layer):
                layer.pop(coord, None)


        elif tool == "spawn_brush":
            already_there = self.spawn_layer.get(coord) == self.spawn_type

            if self._drag_action is None:
                self._drag_action = "remove" if already_there else "add"

            if self._drag_action == "remove":
                if self.spawn_layer.get(coord) == self.spawn_type:
                    self.spawn_layer.pop(coord)
            else:
                # =========================================================
                # Lógica especial para PlatformH (pergunta fase e direção)
                # =========================================================
                if self.spawn_type in ["PlatformH", "PlatformV"]:
                    fase = simpledialog.askfloat("Fase da Plataforma", "Digite a fase inicial (0.0 a 1.0):",
                                                 parent=self.root, minvalue=0.0, maxvalue=1.0)
                    if fase is None:
                        return

                    direcao_str = simpledialog.askstring("Direção Inicial",
                                                         "Digite a direção inicial (esquerda/direita ou cima/baixo):",
                                                         parent=self.root)
                    if direcao_str is None:
                        return

                    # Para horizontal: esquerda = -1, direita = 1
                    # Para vertical: cima = -1, baixo = 1
                    if direcao_str.lower().startswith("e") or direcao_str.lower().startswith("c"):
                        direcao = -1
                    else:
                        direcao = 1

                    self.spawn_layer[coord] = {"type": self.spawn_type, "phase": fase, "direction": direcao}
                else:
                    self.spawn_layer[coord] = self.spawn_type


        elif tool in self.TOOL_LAYERS:
            # wall_brush, block_brush e as 4 rampas: todas seguem a mesma
            # regra de "presença = True". A ação (pintar ou apagar) é
            # decidida uma única vez, no primeiro tile tocado do traço atual
            # (clique ou início do arraste) — clicar em cima de algo já
            # pintado apaga o traço inteiro, clicar no vazio pinta o traço
            # inteiro. Sem isso, cada evento de <B1-Motion> alternava a
            # célula individualmente, e como vários eventos disparam pro
            # mesmo tile enquanto o mouse se move devagar por ele, o
            # resultado piscava entre ligado/desligado de forma imprevisível
            # (era só o Pincel e a Borracha que não sofriam disso, por já
            # serem "sempre seta"/"sempre remove" como os dois casos acima).
            layer = self.TOOL_LAYERS[tool]
            already_there = coord in layer
            if self._drag_action is None:
                self._drag_action = "remove" if already_there else "add"

            if self._drag_action == "remove":
                layer.pop(coord, None)
            else:
                if tool in self.SLOPE_TOOLS:
                    self._clear_slopes(coord)
                layer[coord] = True

        self.draw_grid()

    def on_canvas_press(self, event):
        self._drag_action = None  # começa um traço novo
        self._paint_cell(event)

    def on_canvas_drag(self, event):
        self._paint_cell(event)

    def on_canvas_release(self, event):
        self._drag_action = None  # fim do traço — o próximo clique decide de novo

    def save_map(self):
        try:
            json_data = {
                "width": self.width_var.get(),
                "height": self.height_var.get(),
                "layers": {
                    "terrain": {},
                    "decorations": {},
                    "is_wall": {},
                    "is_block": {},
                    # === NOVAS CAMADAS ===
                    "is_slope_up_right": {},
                    "is_slope_up_left": {},
                    "is_slope_down_right": {},
                    "is_slope_down_left": {},
                    "spawns": {}
                }
            }

            for (col, row), tile_id in self.tile_layer.items():
                json_data["layers"]["terrain"][f"{col},{row}"] = tile_id

            for (col, row), decor_data in self.decoration_layer.items():
                if isinstance(decor_data, dict):
                    json_data["layers"]["decorations"][f"{col},{row}"] = decor_data
                else:
                    # Formato antigo, assume back
                    json_data["layers"]["decorations"][f"{col},{row}"] = {"id": decor_data, "layer": "back"}

            for (col, row) in self.wall_layer:
                json_data["layers"]["is_wall"][f"{col},{row}"] = True

            for (col, row) in self.block_layer:
                json_data["layers"]["is_block"][f"{col},{row}"] = True

            # Salva as rampas
            for layer_name, layer_data in [
                ("is_slope_up_right", self.slope_up_right_layer),
                ("is_slope_up_left", self.slope_up_left_layer),
                ("is_slope_down_right", self.slope_down_right_layer),
                ("is_slope_down_left", self.slope_down_left_layer)
            ]:
                for (col, row) in layer_data:
                    json_data["layers"][layer_name][f"{col},{row}"] = True

            # Salva os spawns (com suporte a dict e string)
            for (col, row), spawn_data in self.spawn_layer.items():
                if isinstance(spawn_data, dict):
                    spawn_type = spawn_data.get("type", "PlatformH")
                    # Remove o "type" antes de salvar
                    spawn_value = {k: v for k, v in spawn_data.items() if k != "type"}
                else:
                    spawn_type = spawn_data
                    spawn_value = True

                if spawn_type not in json_data["layers"]["spawns"]:
                    json_data["layers"]["spawns"][spawn_type] = {}
                json_data["layers"]["spawns"][spawn_type][f"{col},{row}"] = spawn_value

            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=4)
                messagebox.showinfo("Sucesso", f"Mapa salvo em:\n{file_path}")

        except Exception as e:
            # Exibe o erro no console e numa janela (para você ver o que está quebrando)
            print(f"[ERRO] Falha ao salvar: {e}")
            messagebox.showerror("Erro", f"Falha ao salvar o mapa:\n{str(e)}")

    def load_map(self):
        file_path = filedialog.askopenfilename(title="Selecionar Mapa", filetypes=[("JSON files", "*.json")])
        if not file_path: return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.tile_layer.clear()
            self.decoration_layer.clear()
            self.wall_layer.clear()
            self.block_layer.clear()
            self.slope_up_right_layer.clear()
            self.slope_up_left_layer.clear()
            self.slope_down_right_layer.clear()
            self.slope_down_left_layer.clear()
            self.spawn_layer.clear()

            self.width_var.set(data["width"])
            self.height_var.set(data["height"])

            if "terrain" in data["layers"]:
                for coord_str, tile_id in data["layers"]["terrain"].items():
                    col, row = map(int, coord_str.split(','))
                    self.tile_layer[(col, row)] = tile_id

            if "decorations" in data["layers"]:
                for coord_str, decor_data in data["layers"]["decorations"].items():
                    col, row = map(int, coord_str.split(','))
                    if isinstance(decor_data, dict):
                        self.decoration_layer[(col, row)] = decor_data
                    else:
                        # Formato antigo
                        self.decoration_layer[(col, row)] = {"id": decor_data, "layer": "back"}

            if "is_wall" in data["layers"]:
                for coord_str in data["layers"]["is_wall"]:
                    col, row = map(int, coord_str.split(','))
                    self.wall_layer[(col, row)] = True

            if "is_block" in data["layers"]:
                for coord_str in data["layers"]["is_block"]:
                    col, row = map(int, coord_str.split(','))
                    self.block_layer[(col, row)] = True

            # === CARREGANDO RAMPAS ===
            if "is_slope_up_right" in data["layers"]:
                for coord_str in data["layers"]["is_slope_up_right"]:
                    col, row = map(int, coord_str.split(','))
                    self.slope_up_right_layer[(col, row)] = True
            if "is_slope_up_left" in data["layers"]:
                for coord_str in data["layers"]["is_slope_up_left"]:
                    col, row = map(int, coord_str.split(','))
                    self.slope_up_left_layer[(col, row)] = True
            if "is_slope_down_right" in data["layers"]:
                for coord_str in data["layers"]["is_slope_down_right"]:
                    col, row = map(int, coord_str.split(','))
                    self.slope_down_right_layer[(col, row)] = True
            if "is_slope_down_left" in data["layers"]:
                for coord_str in data["layers"]["is_slope_down_left"]:
                    col, row = map(int, coord_str.split(','))
                    self.slope_down_left_layer[(col, row)] = True
            # =========================

            if "spawns" in data["layers"]:
                for spawn_type, coords in data["layers"]["spawns"].items():
                    for coord_str in coords:
                        col, row = map(int, coord_str.split(','))
                        value = coords[coord_str]
                        # ==========================================
                        # Reconstrói o dicionário com "type" para o editor
                        # ==========================================
                        if isinstance(value, dict):
                            value_with_type = dict(value)
                            value_with_type["type"] = spawn_type
                            self.spawn_layer[(col, row)] = value_with_type
                        else:
                            self.spawn_layer[(col, row)] = spawn_type
                        # ==========================================

            self.draw_grid()
            messagebox.showinfo("Sucesso", f"Mapa carregado com sucesso:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar o mapa:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TileEditor(root)
    root.mainloop()