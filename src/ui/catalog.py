import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional
from models.monster import Monster, MonsterSpec
from models.constants import ASSETS_DIR

class CatalogDialog(tk.Toplevel):
    def __init__(self, master, specs: Dict[str, MonsterSpec]):
        super().__init__(master)
        self.title("Catalog")
        self.resizable(False, False)
        self.specs = specs
        self.keys = list(specs.keys())
        self.list = tk.Listbox(self, width=30)
        self.list.pack(side="left", fill="both", expand=True, padx=(8,0), pady=8)
        btns = tk.Frame(self); btns.pack(side="right", fill="y", padx=8, pady=8)
        ttk.Button(btns, text="View Icon", command=self.view_icon).pack(fill="x", pady=2)
        ttk.Button(btns, text="Close", command=self.destroy).pack(fill="x", pady=(8,2))
        for k in self.keys:
            s = specs[k]
            self.list.insert(tk.END, f"{s.name} — {s.element}")

    def selected(self) -> Optional[int]:
        sel = self.list.curselection()
        return sel[0] if sel else None

    def view_icon(self):
        idx = self.selected()
        if idx is None: return
        key = self.keys[idx]
        m = Monster(self.specs[key], level=3)
        IconViewer(self, m)

class IconViewer(tk.Toplevel):
    def __init__(self, master, mon: Monster):
        super().__init__(master)
        self.title(mon.spec.name)
        self.resizable(False, False)
        img = None
        import os
        icon_path = mon.spec.icon
        if icon_path and not os.path.isabs(icon_path):
            if icon_path.startswith("assets/"):
                rel_path = icon_path[len("assets/"):]
                icon_path = os.path.join(ASSETS_DIR, rel_path)
            else:
                icon_path = os.path.join(ASSETS_DIR, icon_path)
        if icon_path and os.path.exists(icon_path):
            try:
                img = tk.PhotoImage(file=icon_path)
            except Exception:
                img = None
        if img is None:
            cv = tk.Canvas(self, width=128, height=128, bg="#222", highlightthickness=0)
            cv.pack(padx=10, pady=10)
            cv.create_rectangle(8,8,120,120, outline="#666")
            cv.create_text(64,64, text=mon.spec.name, fill="#aaa", width=110)
        else:
            w,h = img.width(), img.height()
            ss = max(1, max(w//128, h//128))
            if ss > 1:
                img = img.subsample(ss, ss)
            lbl = tk.Label(self, image=img); lbl.image = img
            lbl.pack(padx=8, pady=8)
        tk.Label(self, text=f"{mon.spec.name} (Lv {mon.level}) — {mon.spec.element}").pack(pady=(0,8))
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=(0,8))
