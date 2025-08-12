import tkinter as tk
from tkinter import ttk
from battle.dialogs import BagDialog
from ui.party import PartyDialog
from ui.catalog import CatalogDialog

class Sidebar(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(borderwidth=0)
        self.money_var = tk.StringVar()
        self.active_var = tk.StringVar()
        tk.Label(self, text="Status", font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        tk.Label(self, textvariable=self.money_var).pack(anchor="w")
        tk.Label(self, textvariable=self.active_var, justify="left").pack(anchor="w", pady=(0,6))

        btnrow = tk.Frame(self)
        btnrow.pack(fill="x", pady=(4,6))
        ttk.Button(btnrow, text="Bag (I)", command=self.open_bag).pack(side="left", expand=True, fill="x")
        ttk.Button(btnrow, text="Party (P)", command=self.open_party).pack(side="left", expand=True, fill="x")
        ttk.Button(btnrow, text="Catalog (C)", command=self.open_catalog).pack(side="left", expand=True, fill="x")

        tips = ("Move: WASD/Arrows\n"
                "Tall grass = more encounters\n"
                "H = heal, C = shop")
        tk.Label(self, text=tips, fg="#aaa").pack(anchor="w")

    def refresh(self, player):
        self.money_var.set(f"Money: {player.money} — Bag: " + ", ".join(f"{k}x{v}" for k,v in player.bag.items()))
        if player.active():
            a = player.active()
            self.active_var.set(f"Active: {a.spec.name} Lv{a.level} [{a.spec.element}]\nHP {a.max_hp}")
        else:
            self.active_var.set("No active monster.")

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
