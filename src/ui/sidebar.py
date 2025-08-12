import tkinter as tk
from tkinter import ttk
from battle.dialogs import BagDialog
from ui.party import PartyDialog
from ui.catalog import CatalogDialog

class Sidebar(tk.Frame):
    def __init__(self, master, width=224, height=1024, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)
        self.configure(borderwidth=0)
        self.pack_propagate(False)

        # Spacer to push buttons and tips to the bottom
        tk.Frame(self).pack(fill="both", expand=True)

        # Button column (bottom, above tips)
        btncol = tk.Frame(self)
        btncol.pack(side="bottom", anchor="s", pady=(0, 24), fill="x")
        btn_style = {"ipadx": 8, "ipady": 8, "padx": 0, "pady": 4, "fill": "x"}
        ttk.Button(btncol, text="Bag (I)", command=self.open_bag).pack(**btn_style)
        ttk.Button(btncol, text="Party (P)", command=self.open_party).pack(**btn_style)
        ttk.Button(btncol, text="Catalog (C)", command=self.open_catalog).pack(**btn_style)
        ttk.Button(btncol, text="Quit", command=self.quit_game).pack(**btn_style)

        # Tips section (bottom)
        tips = ("Move: WASD/Arrows\n"
                "Tall grass = more encounters\n"
                "H = heal, C = shop")
        tk.Label(self, text=tips, fg="#888", font=("TkDefaultFont", 12)).pack(side="bottom", anchor="s", pady=(0, 16))

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
