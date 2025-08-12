from tkinter import messagebox, ttk
import tkinter as tk
from typing import List, Optional
from models.monster import Monster, Combatant

class SwitchDialog(tk.Toplevel):
    def __init__(self, master, party_state: List[Combatant], current_idx: int, on_switch):
        super().__init__(master)
        self.title("Switch Monster")
        self.resizable(False, False)
        self.on_switch = on_switch
        self.party_state = party_state
        self.current_idx = current_idx

        self.list = tk.Listbox(self, width=36)
        self.list.pack(side="left", fill="both", expand=True, padx=(8,0), pady=8)

        btns = tk.Frame(self)
        btns.pack(side="right", fill="y", padx=8, pady=8)
        ttk.Button(btns, text="Switch", command=self.do_switch).pack(fill="x", pady=2)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(fill="x", pady=(8,2))

        for i, c in enumerate(party_state):
            tag = " (active)" if i == current_idx else ""
            status = f"{c.mon.spec.name} Lv{c.mon.level} — HP {c.current_hp}/{c.mon.max_hp}{tag}"
            self.list.insert(tk.END, status)

        # Preselect the first eligible non-active, conscious teammate
        for i, c in enumerate(party_state):
            if i != current_idx and c.current_hp > 0:
                self.list.selection_set(i)
                break

    def do_switch(self):
        sel = self.list.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx == self.current_idx:
            return
        if self.party_state[idx].current_hp <= 0:
            messagebox.showinfo("Switch", "That monster has no HP left!")
            return
        self.destroy()
        self.on_switch(idx)

class BagDialog(tk.Toplevel):
    def __init__(self, master, player):
        super().__init__(master)
        self.title("Bag")
        self.resizable(False, False)
        self.player = player
        frm = tk.Frame(self); frm.pack(padx=10, pady=10)
        for item, qty in player.bag.items():
            tk.Label(frm, text=f"{item}: x{qty}").pack(anchor="w")
        ttk.Button(frm, text="Close", command=self.destroy).pack(pady=(8,0))

class BagUseDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, player, on_use):
        super().__init__(master)
        self.title("Use Item")
        self.resizable(False, False)
        self.player = player
        self.on_use = on_use
        frm = tk.Frame(self); frm.pack(padx=10, pady=10)
        tk.Label(frm, text="Select an item to use:").pack(anchor="w")
        for item, qty in list(player.bag.items()):
            ttk.Button(frm, text=f"{item} x{qty}", command=lambda it=item: self.use(it)).pack(fill="x", pady=2)
        ttk.Button(frm, text="Cancel", command=self.cancel).pack(fill="x", pady=(6,0))

    def use(self, item: str):
        used_capture = False
        if self.player.bag.get(item,0) <= 0:
            messagebox.showinfo("Bag", "You're out of that item.")
            return
        if item == "Charm Orb":
            self.player.bag[item] -= 1
            used_capture = True
            self.destroy(); self.on_use(True, used_capture)
        elif item == "Potion":
            bf = self.master
            heal = min(20, bf.pl.mon.max_hp - bf.pl.current_hp)
            if heal <= 0:
                messagebox.showinfo("Potion", "Already at full HP.")
                return
            bf.pl.current_hp += heal
            self.player.bag[item] -= 1
            self.destroy(); self.on_use(True, used_capture)
        else:
            messagebox.showinfo("Bag", "That item can't be used now.")

    def cancel(self):
        self.destroy(); self.on_use(False, False)