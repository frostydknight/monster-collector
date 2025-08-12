import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional
from models.monster import Monster
from models.constants import ASSETS_DIR

ELEMENT_COLORS = {
    "Water": "#4aa1ff",
    "Fire":  "#ff6b57",
    "Earth": "#a0723a",
    "Air":   "#87d37c",
}

class PartyDialog(tk.Toplevel):
    """Party screen with 6 left-side slots. Each slot shows icon, name, HP, EXP."""
    def __init__(self, master, player):
        super().__init__(master)
        self.title("Party")
        self.resizable(False, False)
        self.player = player
        self.selected = 0   # index 0..5
        self._img_cache = [None] * 6  # keep PhotoImage refs alive
        self._init_party_styles()
        root = tk.Frame(self)
        root.pack(padx=10, pady=10)
        self.slots_frame = tk.Frame(root)
        self.slots_frame.grid(row=0, column=0, sticky="ns")
        self.slot_frames: List[tk.Frame] = []
        for i in range(6):
            f = tk.Frame(self.slots_frame, bd=2, relief="ridge", padx=6, pady=6)
            f.grid(row=i, column=0, sticky="ew", pady=4)
            f.bind("<Button-1>", lambda e, idx=i: self.select(idx))
            self.slot_frames.append(f)
        right = tk.Frame(root)
        right.grid(row=0, column=1, sticky="n", padx=(12, 0))
        self.btn_make_lead = ttk.Button(right, text="Make Lead", command=self.make_lead, width=18)
        self.btn_view_icon = ttk.Button(right, text="View Icon", command=self.view_icon, width=18)
        self.btn_release   = ttk.Button(right, text="Release",   command=self.release,   width=18)
        self.btn_close     = ttk.Button(right, text="Close",     command=self.destroy,   width=18)
        self.btn_make_lead.pack(fill="x", pady=2)
        self.btn_view_icon.pack(fill="x", pady=2)
        self.btn_release.pack(fill="x", pady=8)
        self.btn_close.pack(fill="x")
        self.refresh()

    def _init_party_styles(self):
        style = ttk.Style(self)
        style.configure("PartyName.TLabel", font=("TkDefaultFont", 11, "bold"))
        style.configure("PartySub.TLabel",  font=("TkDefaultFont", 9))
        style.configure("PartySubDim.TLabel", foreground="#7a8aa0", font=("TkDefaultFont", 9))
        style.layout("HP.Horizontal.TProgressbar", style.layout("Horizontal.TProgressbar"))
        style.layout("EXP.Horizontal.TProgressbar", style.layout("Horizontal.TProgressbar"))
        style.configure("HP.Horizontal.TProgressbar",  troughcolor="#29323d", background="#45c36f")
        style.configure("EXP.Horizontal.TProgressbar", troughcolor="#29323d", background="#4aa1ff")
        style.configure("HP.Horizontal.TProgressbar",  troughcolor="#242a33", background="#45c36f")
        style.configure("EXP.Horizontal.TProgressbar", troughcolor="#242a33", background="#4aa1ff")

    def select(self, idx: int):
        self.selected = idx
        self.refresh()

    def _load_icon(self, mon: Monster, maxd: int = 48):
        import os
        icon_path = mon.spec.icon
        if not mon or not icon_path:
            return None
        if not os.path.isabs(icon_path):
            if icon_path.startswith("assets/"):
                rel_path = icon_path[len("assets/"):]
                icon_path = os.path.join(ASSETS_DIR, rel_path)
            else:
                icon_path = os.path.join(ASSETS_DIR, icon_path)
        if not os.path.exists(icon_path):
            return None
        try:
            raw = tk.PhotoImage(file=icon_path)
            w, h = raw.width(), raw.height()
            ss = max(1, max(w // maxd, h // maxd))
            return raw.subsample(ss, ss) if ss > 1 else raw
        except Exception:
            return None

    def refresh(self):
        for i, f in enumerate(self.slot_frames):
            for w in f.winfo_children():
                w.destroy()
            mon = self.player.party[i] if i < len(self.player.party) else None
            is_sel = (i == self.selected)
            f.configure(bg=("#242a33" if is_sel else self.cget("bg")))
            inner = tk.Frame(f, bg=("#242a33" if is_sel else f.cget("bg")), highlightthickness=0)
            inner.pack(fill="x")
            img = self._load_icon(mon) if mon else None
            self._img_cache[i] = img
            icon_lbl = tk.Label(inner, image=img, text=("Empty" if not mon else ""),
                                width=54, bg=inner.cget("bg"), fg="#bbb", compound="center")
            icon_lbl.grid(row=0, column=0, rowspan=3, sticky="w", padx=(0, 8))
            icon_lbl.bind("<Button-1>", lambda e, idx=i: self.select(idx))
            if mon:
                name = f"{mon.spec.name}   Lv{mon.level}"
                name_fg = ELEMENT_COLORS.get(getattr(mon.spec, "element", ""), None)
                name_lbl = tk.Label(inner, text=name, bg=inner.cget("bg"),
                                    font=("TkDefaultFont", 11, "bold"), anchor="w")
                if name_fg:
                    name_lbl.configure(foreground=name_fg)
                name_lbl.grid(row=0, column=1, sticky="w")
                cur_hp = mon.max_hp
                max_hp = mon.max_hp
                hp_pct = int((cur_hp / max_hp) * 100) if max_hp > 0 else 0
                hp_row = tk.Frame(inner, bg=inner.cget("bg"), highlightthickness=0)
                hp_row.grid(row=1, column=1, sticky="we", pady=(2, 0))
                tk.Label(hp_row, text=f"HP: {cur_hp}/{max_hp}", bg=inner.cget("bg")).pack(anchor="w")
                ttk.Progressbar(hp_row, style="HP.Horizontal.TProgressbar",
                                orient="horizontal", length=160, mode="determinate",
                                maximum=100, value=hp_pct).pack(anchor="w")
                exp_now = mon.exp
                exp_next = mon.exp_to_next()
                exp_pct = int((exp_now / exp_next) * 100) if exp_next > 0 else 0
                exp_row = tk.Frame(inner, bg=inner.cget("bg"), highlightthickness=0)
                exp_row.grid(row=2, column=1, sticky="we", pady=(2, 0))
                tk.Label(exp_row, text=f"EXP: {exp_now}/{exp_next}", bg=inner.cget("bg"), fg="#7a8aa0").pack(anchor="w")
                ttk.Progressbar(exp_row, style="EXP.Horizontal.TProgressbar",
                                orient="horizontal", length=160, mode="determinate",
                                maximum=100, value=exp_pct).pack(anchor="w")
            else:
                tk.Label(inner, text="— empty —", bg=inner.cget("bg"), fg="#7a8aa0").grid(row=0, column=1, sticky="w")
                tk.Label(inner, text="HP: —",      bg=inner.cget("bg"), fg="#7a8aa0").grid(row=1, column=1, sticky="w")
                tk.Label(inner, text="EXP: —",     bg=inner.cget("bg"), fg="#7a8aa0").grid(row=2, column=1, sticky="w")
        have_mon = self.selected < len(self.player.party)
        self.btn_make_lead.configure(state=("normal" if have_mon and self.selected != 0 else "disabled"))
        self.btn_view_icon.configure(state=("normal" if have_mon else "disabled"))
        self.btn_release.configure(state=("normal" if have_mon else "disabled"))

    def selected_index(self) -> Optional[int]:
        return self.selected if self.selected < len(self.player.party) else None

    def view_icon(self):
        idx = self.selected_index()
        if idx is None: return
        m = self.player.party[idx]
        from ui.catalog import IconViewer
        IconViewer(self, m)

    def make_lead(self):
        idx = self.selected_index()
        if idx is None or idx == 0: return
        self.player.party[0], self.player.party[idx] = self.player.party[idx], self.player.party[0]
        self.refresh()
        if hasattr(self.master, "update_sidebar"):
            self.master.update_sidebar()

    def release(self):
        idx = self.selected_index()
        if idx is None: return
        m = self.player.party.pop(idx)
        messagebox.showinfo("Release", f"Released {m.spec.name}.")
        if self.selected >= len(self.player.party):
            self.selected = max(0, len(self.player.party) - 1)
        self.refresh()
        if hasattr(self.master, "update_sidebar"):
            self.master.update_sidebar()
