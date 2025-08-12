import json
import os
import tkinter as tk
from models.constants import ASSETS_DIR

class TileIconManager:
    def __init__(self, tile_size: int):
        self.tile_size = tile_size
        self.icon_map = {}       # symbol -> PhotoImage (scaled)
        self.overlays = []       # list of dicts: {x, y, icon(PhotoImage)}
        self._raw_cache = {}     # path -> raw PhotoImage

    def _load_raw(self, path: str):
        if not path:
            return None
        # If path is not absolute, resolve it relative to ASSETS_DIR
        if not os.path.isabs(path):
            if path.startswith("assets/"):
                rel_path = path[len("assets/"):]
                abs_path = os.path.join(ASSETS_DIR, rel_path)
            else:
                abs_path = os.path.join(ASSETS_DIR, path)
        else:
            abs_path = path
        if not os.path.exists(abs_path):
            return None
        if abs_path in self._raw_cache:
            return self._raw_cache[abs_path]
        try:
            img = tk.PhotoImage(file=abs_path)
            self._raw_cache[abs_path] = img
            return img
        except Exception:
            return None

    def _scale_to_tile(self, img: "tk.PhotoImage"):
        # Integer downscale to fit TILE while keeping aspect
        if not img:
            return None
        w, h = img.width(), img.height()
        if w <= self.tile_size and h <= self.tile_size:
            return img
        ss = max(1, max(w // self.tile_size, h // self.tile_size))
        return img.subsample(ss, ss)

    def load_from_json(self, json_path: str):
        # Example schema:
        # {
        #   "symbols": { "H": "assets/tiles/hut.png", "C":"assets/tiles/shop.png" },
        #   "overlays": [ {"x":10,"y":3,"icon":"assets/tiles/sign.png"} ]
        # }
        if not os.path.exists(json_path):
            return  # silent if missing
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return

        # Load symbol icons
        for sym, path in (data.get("symbols") or {}).items():
            raw = self._load_raw(path)
            scaled = self._scale_to_tile(raw) if raw else None
            if scaled:
                self.icon_map[sym] = scaled

        # Load overlays
        self.overlays.clear()
        for entry in (data.get("overlays") or []):
            path = entry.get("icon")
            raw = self._load_raw(path)
            scaled = self._scale_to_tile(raw) if raw else None
            if scaled is not None and "x" in entry and "y" in entry:
                self.overlays.append({"x": int(entry["x"]), "y": int(entry["y"]), "img": scaled})

    def get_symbol_icon(self, ch: str):
        return self.icon_map.get(ch)

    def get_overlays(self):
        return list(self.overlays)

def redraw_map(canvas, world_map, tile_size, tile_icons, player, trainers=None):
    c = canvas
    c.delete("all")
    for y, row in enumerate(world_map):
        for x, ch in enumerate(row):
            x0, y0 = x * tile_size, y * tile_size
            x1, y1 = x0 + tile_size, y0 + tile_size
            if ch == '#':
                c.create_rectangle(x0, y0, x1, y1, fill="#3a3a3a", outline="#2a2a2a")
                sym_img = tile_icons.get_symbol_icon(ch) if tile_icons else None
                if sym_img:
                    c.create_image(x0 + tile_size//2, y0 + tile_size//2, image=sym_img)
            elif ch == 'T':
                c.create_rectangle(x0, y0, x1, y1, fill="#2f5d34", outline="#244a29")
                c.create_line(x0+6, y1-6, x1-6, y0+6, fill="#26572b")
                sym_img = tile_icons.get_symbol_icon(ch) if tile_icons else None
                if sym_img:
                    c.create_image(x0 + tile_size//2, y0 + tile_size//2, image=sym_img)
            elif ch == 'H':
                c.create_rectangle(x0, y0, x1, y1, fill="#2c3e50", outline="#1f2d3a")
                c.create_text((x0+x1)//2, (y0+y1)//2, text='H', fill='white')
                sym_img = tile_icons.get_symbol_icon(ch) if tile_icons else None
                if sym_img:
                    c.create_image(x0 + tile_size//2, y0 + tile_size//2, image=sym_img)
            elif ch == 'C':
                c.create_rectangle(x0, y0, x1, y1, fill="#6d4c41", outline="#4e382f")
                c.create_text((x0+x1)//2, (y0+y1)//2, text='C', fill='white')
                sym_img = tile_icons.get_symbol_icon(ch) if tile_icons else None
                if sym_img:
                    c.create_image(x0 + tile_size//2, y0 + tile_size//2, image=sym_img)
            elif ch == 'E':
                c.create_rectangle(x0, y0, x1, y1, fill="#8e44ad", outline="#6c3483")
                c.create_text((x0+x1)//2, (y0+y1)//2, text='E', fill='white')
                sym_img = tile_icons.get_symbol_icon(ch) if tile_icons else None
                if sym_img:
                    c.create_image(x0 + tile_size//2, y0 + tile_size//2, image=sym_img)
            else:
                c.create_rectangle(x0, y0, x1, y1, fill="#2b2b2b", outline="#222")
                sym_img = tile_icons.get_symbol_icon(ch) if tile_icons else None
                if sym_img:
                    c.create_image(x0 + tile_size//2, y0 + tile_size//2, image=sym_img)
    px, py = player.x, player.y
    c.create_oval(px*tile_size+6, py*tile_size+6, px*tile_size+tile_size-6, py*tile_size+tile_size-6, fill="#cddc39", outline="#9e9d24")
    # draw trainers (not defeated)
    if trainers:
        for tr in trainers:
            if getattr(tr, 'defeated', False):
                continue
            x0, y0 = tr.x * tile_size, tr.y * tile_size
            c.create_rectangle(x0+6, y0+6, x0+tile_size-6, y0+tile_size-6,
                                outline="#ff6961", fill="", width=2)
            c.create_text(x0+tile_size//2, y0+tile_size//2, text='R', fill='#ff6961')  # R = trainer
    # Per-coordinate overlays (decorations/objects)
    if tile_icons:
        for ov in tile_icons.get_overlays():
            x0, y0 = ov["x"] * tile_size, ov["y"] * tile_size
            c.create_image(x0 + tile_size//2, y0 + tile_size//2, image=ov["img"])

def tile_at(x: int, y: int, world_map) -> str:
    if 0 <= y < len(world_map) and 0 <= x < len(world_map[0]):
        return world_map[y][x]
    return '#'
