import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import json
import os


class OverworldEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Super Mario World - Overworld Editor")
        self.root.geometry("1100x700")
        self.root.configure(bg="#2b2b2b")

        self.TILE_SIZE = 32
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.EXPORT_DIR = os.path.join(self.BASE_DIR, 'game', 'assets', 'overworld_export')
        self.TERRAIN_DIR = os.path.join(self.EXPORT_DIR, 'terrain')

        # Camadas
        self.terrain_layer = {}
        self.path_layer = {}
        self.nodes_layer = {}  # { (col, row): {"type": "Level", "level_file": "..."} }

        self.tile_images = {}
        self.tile_buttons = {}
        self.selected_tile_id = None

        self.grid_width = 50
        self.grid_height = 30
        self.current_tool = "brush"
        self.selected_node = None

        self.setup_ui()
        self.load_tiles()
        self.draw_grid()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_frame, width=430, bg="#3c3c3c")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)

        top_frame = tk.Frame(left_frame, bg="#3c3c3c")
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 5))
        tk.Label(top_frame, text="FERRAMENTAS", bg="#3c3c3c", fg="white", font=("Arial", 12, "bold")).pack()

        btn_frame = tk.Frame(top_frame, bg="#3c3c3c")
        btn_frame.pack(pady=5)

        # Linha 1: Pincel, Borracha e Caminho
        tk.Button(btn_frame, text="Pincel", bg="#90EE90", command=lambda: self.set_tool("brush"), width=8).grid(row=0,
                                                                                                                column=0,
                                                                                                                padx=2,
                                                                                                                pady=2)
        tk.Button(btn_frame, text="Borracha", bg="#FF9999", command=lambda: self.set_tool("erase"), width=8).grid(row=0,
                                                                                                                  column=1,
                                                                                                                  padx=2,
                                                                                                                  pady=2)
        tk.Button(btn_frame, text="Caminho", bg="#87CEFA", fg="black", command=lambda: self.set_tool("path_brush"),
                  width=8).grid(row=0, column=2, padx=2, pady=2)

        # Linha 2: Marcador de Nó e Dropdown
        tk.Label(btn_frame, text="Tipo de Nó:", bg="#3c3c3c", fg="white", font=("Arial", 9)).grid(row=1, column=0,
                                                                                                  pady=(5, 0))

        self.node_type_var = tk.StringVar(value="Level")
        node_combo = ttk.Combobox(btn_frame, textvariable=self.node_type_var,
                                  values=["Spawn", "Level", "CastleSmall", "CastleMedium", "CastleLarge",
                                          "CastleBoss", "CastleFinal", "Cave", "Water", "GhostHouse"],
                                  width=12, state="readonly")
        node_combo.grid(row=1, column=1, columnspan=2, pady=(5, 0))

        tk.Button(btn_frame, text="Marcador de Nó", bg="#FFD700", fg="black",
                  command=lambda: self.set_tool("node_brush"), width=18).grid(row=2, column=0, columnspan=3, pady=5)

        # --- ABAS (Apenas Terreno) ---
        tile_container = tk.Frame(left_frame, bg="#3c3c3c")
        tile_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(10, 0))
        tk.Label(tile_container, text="PALETA DE TERRENO", bg="#3c3c3c", fg="white", font=("Arial", 12, "bold")).pack()

        self.notebook = ttk.Notebook(tile_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.category_widgets = {}
        # Carrega apenas a aba do Terreno
        frame = tk.Frame(self.notebook, bg="#505050")
        self.notebook.add(frame, text="Terreno")

        canvas = tk.Canvas(frame, bg="#505050", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = tk.Frame(canvas, bg="#505050")
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.category_widgets["terrain"] = {"frame": inner_frame, "canvas": canvas}

        # --- ÁREA INFERIOR ---
        bottom_frame = tk.Frame(left_frame, bg="#3c3c3c")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)

        tk.Label(bottom_frame, text="TAMANHO DO MAPA", bg="#3c3c3c", fg="white", font=("Arial", 10, "bold")).pack()
        size_frame = tk.Frame(bottom_frame, bg="#3c3c3c")
        size_frame.pack(pady=5)

        tk.Label(size_frame, text="Largura:", bg="#3c3c3c", fg="white").pack(side=tk.LEFT, padx=5)
        self.width_var = tk.IntVar(value=50)
        tk.Spinbox(size_frame, from_=10, to=200, textvariable=self.width_var, width=5).pack(side=tk.LEFT)

        tk.Label(size_frame, text="Altura:", bg="#3c3c3c", fg="white").pack(side=tk.LEFT, padx=5)
        self.height_var = tk.IntVar(value=30)
        tk.Spinbox(size_frame, from_=10, to=200, textvariable=self.height_var, width=5).pack(side=tk.LEFT)

        self.width_var.trace_add("write", self.update_grid_size)
        self.height_var.trace_add("write", self.update_grid_size)

        tk.Button(bottom_frame, text="CARREGAR OVERWORLD (.json)", bg="#4682B4", fg="white",
                  font=("Arial", 10, "bold"), command=self.load_map).pack(pady=(5, 2), fill=tk.X)
        tk.Button(bottom_frame, text="SALVAR OVERWORLD (.json)", bg="#228B22", fg="white",
                  font=("Arial", 10, "bold"), command=self.save_map).pack(pady=5, fill=tk.X)

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
            self.grid_width = self.width_var.get()
            self.grid_height = self.height_var.get()
            if self.grid_width < 1: self.grid_width = 1
            if self.grid_height < 1: self.grid_height = 1
            self.draw_grid()
        except tk.TclError:
            pass

    def load_tiles(self):
        if not os.path.exists(self.TERRAIN_DIR):
            messagebox.showerror("Erro", f"Pasta 'terrain' não encontrada!\nExecute o novo script de extração.")
            return

        dir_path = self.TERRAIN_DIR
        widgets = self.category_widgets["terrain"]
        frame = widgets["frame"]
        canvas = widgets["canvas"]

        for widget in frame.winfo_children():
            widget.destroy()

        files = sorted([f for f in os.listdir(dir_path) if f.endswith('.png')])

        col_count = 0
        row_count = 0
        max_cols = 10

        for filename in files:
            tile_id = filename.replace('.png', '')
            filepath = os.path.join(dir_path, filename)

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
        self.selected_node = None

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

        # Grade
        for x in range(0, w + 1, self.TILE_SIZE):
            self.canvas.create_line(x, 0, x, h, fill="#505050", width=1)
        for y in range(0, h + 1, self.TILE_SIZE):
            self.canvas.create_line(0, y, w, y, fill="#505050", width=1)

        # 1. Terreno
        for (col, row), tile_id in self.terrain_layer.items():
            if tile_id in self.tile_images:
                x = col * self.TILE_SIZE
                y = row * self.TILE_SIZE
                self.canvas.create_image(x, y, anchor=tk.NW, image=self.tile_images[tile_id])

        # 2. Caminhos
        for (col, row) in self.path_layer:
            x = col * self.TILE_SIZE
            y = row * self.TILE_SIZE
            self.canvas.create_rectangle(x, y, x + self.TILE_SIZE, y + self.TILE_SIZE,
                                         fill="#87CEFA", stipple="gray50", outline="#4682B4", width=2)

        # 3. Nós (Agora são quadrados coloridos com símbolos)
        spawn_symbols = {
            "Spawn": "S", "Level": "L", "CastleSmall": "C",
            "CastleMedium": "M", "CastleLarge": "B", "CastleBoss": "K",
            "CastleFinal": "F", "Cave": "V", "Water": "W", "GhostHouse": "G"
        }

        for (col, row), node_data in self.nodes_layer.items():
            node_type = node_data.get("type", "Level")
            x = col * self.TILE_SIZE
            y = row * self.TILE_SIZE

            # Desenha o marcador (verde para spawns, roxo escuro para níveis, outros para castelos)
            if node_type == "Spawn":
                fill_color, outline_color = "#00FF00", "#006400"
            elif node_type == "CastleBoss" or node_type == "CastleFinal":
                fill_color, outline_color = "#FF4500", "#8B0000"
            else:
                fill_color, outline_color = "#4B0082", "#8A2BE2"

            self.canvas.create_rectangle(x, y, x + self.TILE_SIZE, y + self.TILE_SIZE,
                                         fill=fill_color, stipple="gray50", outline=outline_color, width=2)

            symbol = spawn_symbols.get(node_type, "N")
            self.canvas.create_text(x + self.TILE_SIZE // 2, y + self.TILE_SIZE // 2,
                                    text=symbol, fill="white", font=("Arial", 12, "bold"))

            if self.selected_node == (col, row):
                self.canvas.create_rectangle(x, y, x + self.TILE_SIZE, y + self.TILE_SIZE, outline="#FFD700", width=4)

    def _paint_cell(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        col = int(x // self.TILE_SIZE)
        row = int(y // self.TILE_SIZE)
        if col >= self.grid_width or row >= self.grid_height or col < 0 or row < 0:
            return

        coord = (col, row)

        if self.current_tool == "brush":
            if self.selected_tile_id:
                self.terrain_layer[coord] = self.selected_tile_id

        elif self.current_tool == "erase":
            self.terrain_layer.pop(coord, None)
            self.path_layer.pop(coord, None)
            self.nodes_layer.pop(coord, None)

        elif self.current_tool == "path_brush":
            if (col, row) in self.path_layer:
                self.path_layer.pop((col, row))
            else:
                self.path_layer[(col, row)] = True

        elif self.current_tool == "node_brush":
            node_type = self.node_type_var.get()
            if coord in self.nodes_layer:
                # Se clicar em cima de um nó já existente, abre a edição
                self.selected_node = coord
                self.edit_node_properties()
            else:
                # Cria um novo nó
                import uuid
                self.nodes_layer[coord] = {
                    "uid": str(uuid.uuid4())[:8],
                    "type": node_type,
                    "level_file": "placeholder.json"
                }
                self.selected_node = coord

        self.draw_grid()

    def edit_node_properties(self):
        if self.selected_node not in self.nodes_layer:
            return

        node_data = self.nodes_layer[self.selected_node]
        current_file = node_data.get("level_file", "placeholder.json")
        current_order = node_data.get("order", 0)
        current_music = node_data.get("music", "overworld")  # Padrão overworld se não configurado

        new_file = simpledialog.askstring(
            "Propriedades do Nó",
            f"Digite o nome do arquivo de fase (.json):\n(Atual: {current_file})",
            initialvalue=current_file
        )

        if new_file is not None:
            if new_file.strip() == "":
                node_data["level_file"] = "placeholder.json"
            else:
                node_data["level_file"] = new_file

            new_order = simpledialog.askinteger(
                "Ordem do Nó",
                "Digite a ordem de desbloqueio do nó (0 é o primeiro nível):",
                initialvalue=current_order,
                minvalue=0,
                maxvalue=99
            )
            if new_order is not None:
                node_data["order"] = new_order

            # =======================================================
            # NOVO: Pergunta a música da fase
            # =======================================================
            new_music = simpledialog.askstring(
                "Música da Fase",
                "Digite o nome da música (sem extensão .ogg):\n(Ex: overworld, underground, castle, athletic)",
                initialvalue=current_music
            )
            if new_music is not None:
                if new_music.strip() == "":
                    node_data["music"] = "overworld"  # Fallback para não quebrar
                else:
                    node_data["music"] = new_music.strip()
            # =======================================================

            self.draw_grid()

    def on_canvas_press(self, event):
        self._paint_cell(event)

    def on_canvas_drag(self, event):
        self._paint_cell(event)

    def on_canvas_release(self, event):
        pass

    def save_map(self):
        json_data = {
            "width": self.grid_width,
            "height": self.grid_height,
            "layers": {
                "terrain": {},
                "paths": {},
                "nodes": {}
            }
        }

        for (col, row), tile_id in self.terrain_layer.items():
            json_data["layers"]["terrain"][f"{col},{row}"] = tile_id

        for (col, row) in self.path_layer:
            json_data["layers"]["paths"][f"{col},{row}"] = True

        for (col, row), node_data in self.nodes_layer.items():
            json_data["layers"]["nodes"][f"{col},{row}"] = node_data

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4)
            messagebox.showinfo("Sucesso", f"Overworld salvo em:\n{file_path}")

    def load_map(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar Overworld",
            filetypes=[("JSON files", "*.json")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.terrain_layer.clear()
            self.path_layer.clear()
            self.nodes_layer.clear()
            self.selected_node = None

            self.width_var.set(data.get("width", 50))
            self.height_var.set(data.get("height", 30))
            self.grid_width = self.width_var.get()
            self.grid_height = self.height_var.get()

            if "terrain" in data["layers"]:
                for coord_str, tile_id in data["layers"]["terrain"].items():
                    col, row = map(int, coord_str.split(','))
                    self.terrain_layer[(col, row)] = tile_id

            if "paths" in data["layers"]:
                for coord_str in data["layers"]["paths"]:
                    col, row = map(int, coord_str.split(','))
                    self.path_layer[(col, row)] = True

            if "nodes" in data["layers"]:
                for coord_str, node_data in data["layers"]["nodes"].items():
                    col, row = map(int, coord_str.split(','))
                    self.nodes_layer[(col, row)] = node_data

            self.draw_grid()
            messagebox.showinfo("Sucesso", f"Overworld carregado com sucesso:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar o mapa:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = OverworldEditor(root)
    root.mainloop()