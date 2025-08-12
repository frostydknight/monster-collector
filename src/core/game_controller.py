import os
import random
from typing import List, Tuple
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from models.monster import Monster
from models.player import Player
from models.constants import WORLD_MAP, ASSETS_DIR, TILE, TILE_ICONS_JSON, CANVAS_W, CANVAS_H, MAP_W, MAP_H, SIDEBAR_W, SIDEBAR_H
from models.trainer import Trainer, create_trainers, tile_in_front_of_trainer, check_trainer_engagement, on_trainer_defeated
from battle.dialogs import BagDialog
from ui.sidebar import Sidebar
from ui.catalog import CatalogDialog
from ui.shop import ShopDialog
from ui.party import PartyDialog
from core.map_manager import TileIconManager, redraw_map, tile_at
from data.loader import load_monster_db, load_player_from_profile, save_profile
from battle.manager import BattleManager
from ui.main_menu.main_menu import MainMenu

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide main window until profile is loaded
        self.profile = None
        self.menu = MainMenu(self, self.on_profile_loaded)
        self.wait_window(self.menu)
        if not self.profile:
            self.destroy()
            return
        self.deiconify()  # Show main window
        self.title("Monster Collector — Tkinter Edition")
        self.resizable(False, False)
        os.makedirs(os.path.join(ASSETS_DIR, "monsters"), exist_ok=True)

        self.in_battle = False

        # Game state
        self.specs = load_monster_db()
        # Load player from profile or create new
        if self.profile.get('data'):
            self.player = load_player_from_profile(self.profile)
        else:
            self.player = Player()
            starter_key = random.choice(list(self.specs.keys()))
            self.player.party.append(Monster(self.specs[starter_key], level=3))
        self.trainers: List[Trainer] = create_trainers()

        # Overworld UI
        # Load map background image
        map_bg_path = os.path.join(ASSETS_DIR, "ui", "map_bg.png")
        if os.path.exists(map_bg_path):
            pil_img = Image.open(map_bg_path).resize((MAP_W, MAP_H))
            self.map_bg_image = ImageTk.PhotoImage(pil_img)
            self.map_bg_label = tk.Label(self, image=self.map_bg_image, borderwidth=0, highlightthickness=0)
            self.map_bg_label.place(x=0, y=0, width=MAP_W, height=MAP_H)
            self.map_bg_label.lower()

        # Place the map canvas above the background image
        self.map_canvas = tk.Canvas(self, width=MAP_W, height=MAP_H, highlightthickness=0, borderwidth=0, bg='#000000')
        self.map_canvas.place(x=0, y=0, width=MAP_W, height=MAP_H)

        self.sidebar = Sidebar(self, width=SIDEBAR_W, height=SIDEBAR_H)
        self.sidebar.place(x=MAP_W, y=0, width=SIDEBAR_W, height=SIDEBAR_H)

        # Tile icons
        os.makedirs(os.path.join(ASSETS_DIR, "tiles"), exist_ok=True)
        self.tile_icons = TileIconManager(TILE)
        self.tile_icons.load_from_json(TILE_ICONS_JSON)


        self.bind_all("<Key>", self.on_key)
        self.redraw_map()
        self.update_sidebar()

    # ------------- Rendering -------------
    def redraw_map(self):
        redraw_map(self.map_canvas, WORLD_MAP, TILE, self.tile_icons, self.player, self.trainers)

    def tile_at(self, x: int, y: int) -> str:
        return tile_at(x, y, WORLD_MAP)

    def update_sidebar(self):
        self.sidebar.refresh(self.player)

    # ------------- Input -------------
    def on_key(self, ev):
        if self.in_battle:
            return
        key = ev.keysym.lower()
        if key in ("w","a","s","d","up","down","left","right"):
            dx = dy = 0
            if key in ("w","up"): dy = -1
            if key in ("s","down"): dy = 1
            if key in ("a","left"): dx = -1
            if key in ("d","right"): dx = 1
            self.try_move(dx, dy)
        elif key == 'i':
            BagDialog(self, self.player)
        elif key == 'p':
            PartyDialog(self, self.player)
        elif key == 'c':
            CatalogDialog(self, self.specs)
        elif key == 'h':
            messagebox.showinfo("Help", "WASD/Arrows to move.\nI: Bag, P: Party, C: Catalog.\nH tiles heal, C tiles are shop.")

    def try_move(self, dx: int, dy: int):
        nx, ny = self.player.x + dx, self.player.y + dy
        if self.tile_at(nx, ny) != '#':
            self.player.x, self.player.y = nx, ny
            self.redraw_map()
            self.update_sidebar()
            self.check_tile_event()
            self.check_trainer_engagement()

            t = self.tile_at(self.player.x, self.player.y)
            if t in {'.','T',' '} and self.player.party:
                base = 0.08 if t == '.' else (0.16 if t == 'T' else 0.04)
                if random.random() < base:
                    self.start_wild_battle()

    def check_tile_event(self):
        t = self.tile_at(self.player.x, self.player.y)
        if t == 'H':
            self.heal_party()
            messagebox.showinfo("Hut", "Your party is fully refreshed!")
        elif t == 'C':
            ShopDialog(self, self.player)

    # ------------- Battle -------------
    def start_wild_battle(self):
        BattleManager.start_wild_battle(self)

    def random_wild(self) -> Monster:
        return BattleManager.random_wild(self)

    def heal_party(self):
        BattleManager.heal_party(self)

    def tile_in_front_of_trainer(self, tr: Trainer) -> Tuple[int, int]:
        return tile_in_front_of_trainer(tr)

    def check_trainer_engagement(self):
        check_trainer_engagement(self)

    def on_trainer_defeated(self, trainer: Trainer):
        on_trainer_defeated(self, trainer)

    def on_profile_loaded(self, profile):
        self.profile = profile

    def save_game(self):
        if self.profile:
            save_profile(self.profile, self.player)

    def on_closing(self):
        self.save_game()
        self.destroy()
