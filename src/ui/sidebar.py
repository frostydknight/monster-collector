import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from battle.dialogs import BagDialog
from ui.party import PartyDialog
from ui.catalog import CatalogDialog
import os

class Sidebar(tk.Frame):
    def __init__(self, master, width=224, height=1024, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)
        self.configure(borderwidth=0, highlightthickness=0)
        self.pack_propagate(False)

        # Load sidebar background image
        sidebar_bg_path = os.path.join(os.path.dirname(__file__), '../assets/ui/sidebar_bg.png')
        sidebar_bg_path = os.path.abspath(sidebar_bg_path)
        if os.path.exists(sidebar_bg_path):
            pil_img = Image.open(sidebar_bg_path).resize((width, height))
            self.bg_image = ImageTk.PhotoImage(pil_img)
            self.bg_label = tk.Label(self, image=self.bg_image, borderwidth=0)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()

        # Place tips label near the bottom
        tips = ("Move: WASD/Arrows\n"
                "Tall grass = more encounters\n"
                "H = heal, C = shop")
        self.tips_label = tk.Label(self, text=tips, fg="#888", font=("TkDefaultFont", 12), borderwidth=0, highlightthickness=0)
        self.tips_label.place(x=10, y=height-160, width=width-20, height=60)

        # Place buttons above the tips
        btn_y_start = height-90
        btn_height = 40
        btn_spacing = 8
        btn_width = width-24
        self.bag_btn = ttk.Button(self, text="Bag (I)", command=self.open_bag)
        self.bag_btn.place(x=12, y=btn_y_start, width=btn_width, height=btn_height)
        self.party_btn = ttk.Button(self, text="Party (P)", command=self.open_party)
        self.party_btn.place(x=12, y=btn_y_start+btn_height+btn_spacing, width=btn_width, height=btn_height)
        self.catalog_btn = ttk.Button(self, text="Catalog (C)", command=self.open_catalog)
        self.catalog_btn.place(x=12, y=btn_y_start+2*(btn_height+btn_spacing), width=btn_width, height=btn_height)
        self.quit_btn = ttk.Button(self, text="Quit", command=self.quit_game)
        self.quit_btn.place(x=12, y=btn_y_start+3*(btn_height+btn_spacing), width=btn_width, height=btn_height)

    def refresh(self, player):
        pass

    def open_bag(self):
        if hasattr(self.master, 'open_bag'):
            self.master.open_bag()
        else:
            BagDialog(self, getattr(self.master, 'player', None))

    def open_party(self):
        if hasattr(self.master, 'open_party'):
            self.master.open_party()
        else:
            PartyDialog(self, getattr(self.master, 'player', None))

    def open_catalog(self):
        if hasattr(self.master, 'open_catalog'):
            self.master.open_catalog()
        else:
            CatalogDialog(self, getattr(self.master, 'specs', {}))
    
    def update_sidebar(self):
        self.master.update_sidebar()

    def quit_game(self):
        if hasattr(self.master, 'on_closing'):
            self.master.on_closing()
        else:
            self.master.destroy()
