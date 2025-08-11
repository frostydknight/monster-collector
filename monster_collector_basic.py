#!/usr/bin/env python3
"""
Monster Collector — Tkinter Edition
-----------------------------------
Single-file, minimal-dependency (Tkinter only) Pokémon-like prototype with:
- Windowed UI (Tkinter)
- Tile-based overworld map on a Canvas
- Random encounters with on-canvas battle UI (buttons, no enter-spam)
- Capture system (Charm Orbs)
- Party & Catalog viewers with optional PNG/GIF icons
- Healing hut and shop
- monsters.json database (auto-created on first run, editable), supports per-monster icon paths

Run:
    python monster_collector_tk.py

Notes:
- Uses only the Python standard library (tkinter)
- PNG/GIF icons recommended (placed under ./assets/monsters). See monsters.json "icon" field
- Designed for clarity and hackability over performance
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ------------------ Constants & Data ------------------

WORLD_MAP = [
    "########################",
    "#......TT....####.....H#",
    "#..####..##..#..#..TT..#",
    "#..#  #..#...#..#..##..#",
    "#..#  #..####..#.......#",
    "#..#  #........#..TT...#",
    "#..####..TTTT..##..###..#",
    "#.............C.....#..##",
    "#..TT..######..TT..#..TT#",
    "#......#....#......#....#",
    "########################",
]
# Legend:
# . = plain, T = tall grass, # = wall, H = healing hut, C = shop, ' ' = path

TILE = 28  # tile size in pixels
CANVAS_W = len(WORLD_MAP[0]) * TILE
CANVAS_H = len(WORLD_MAP) * TILE

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
MONSTER_JSON = os.path.join(os.path.dirname(__file__), "monsters.json")

# Default DB written on first run
DEFAULT_MONSTERS = {
    "slime_girl": {
        "name": "Slime Girl",
        "element": "Water",
        "base_hp": 20,
        "base_atk": 8,
        "base_def": 6,
        "base_spd": 7,
        "catch_rate": 190,
        "icon": "assets/monsters/slime_girl.png",
        "learnset": [
            {"name": "Splash Kiss", "power": 30, "accuracy": 0.95},
            {"name": "Ooze Slam", "power": 40, "accuracy": 0.9},
        ],
    },
    "harpy": {
        "name": "Harpy",
        "element": "Air",
        "base_hp": 22,
        "base_atk": 9,
        "base_def": 6,
        "base_spd": 12,
        "catch_rate": 160,
        "icon": "assets/monsters/harpy.png",
        "learnset": [
            {"name": "Gust Peck", "power": 35, "accuracy": 0.95},
            {"name": "Sky Rake", "power": 45, "accuracy": 0.88},
        ],
    },
    "minotaur": {
        "name": "Minotaur",
        "element": "Earth",
        "base_hp": 28,
        "base_atk": 12,
        "base_def": 10,
        "base_spd": 6,
        "catch_rate": 120,
        "icon": "assets/monsters/minotaur.png",
        "learnset": [
            {"name": "Horn Bash", "power": 40, "accuracy": 0.95},
            {"name": "Labyrinth Rush", "power": 50, "accuracy": 0.85},
        ],
    },
}

ELEMENT_EFFECTIVENESS = {
    ("Water", "Fire"): 1.5,
    ("Fire", "Earth"): 1.5,
    ("Earth", "Air"): 1.5,
    ("Air", "Water"): 1.5,
}

# ------------------ Models ------------------

@dataclass
class Move:
    name: str
    power: int
    accuracy: float
    kind: str = "physical"

@dataclass
class MonsterSpec:
    key: str
    name: str
    element: str
    base_hp: int
    base_atk: int
    base_def: int
    base_spd: int
    catch_rate: int
    icon: Optional[str] = None
    learnset: List[Move] = field(default_factory=list)

@dataclass
class Monster:
    spec: MonsterSpec
    level: int = 3
    exp: int = 0
    moves: List[Move] = field(default_factory=list)

    def __post_init__(self):
        if not self.moves:
            self.moves = self.spec.learnset[:2] if self.spec.learnset else [Move("Tackle", 35, 0.95)]

    @property
    def max_hp(self) -> int:
        return max(1, int(self.spec.base_hp + self.level * 3))

    @property
    def atk(self) -> int:
        return max(1, int(self.spec.base_atk + self.level * 2))

    @property
    def defense(self) -> int:
        return max(1, int(self.spec.base_def + self.level * 2))

    @property
    def speed(self) -> int:
        return max(1, int(self.spec.base_spd + int(self.level * 1.5)))

    def exp_to_next(self) -> int:
        return 20 + self.level * 10

    def gain_exp(self, amount: int) -> List[str]:
        logs = [f"{self.spec.name} gained {amount} EXP!"]
        self.exp += amount
        while self.exp >= self.exp_to_next():
            self.exp -= self.exp_to_next()
            self.level += 1
            logs.append(f"{self.spec.name} leveled up to {self.level}!")
        return logs

# ------------------ Helpers ------------------

def ensure_default_monsters_file():
    if not os.path.exists(MONSTER_JSON):
        os.makedirs(os.path.dirname(MONSTER_JSON), exist_ok=True)
        with open(MONSTER_JSON, "w", encoding="utf-8") as f:
            json.dump({"monsters": DEFAULT_MONSTERS}, f, indent=2)


def load_monster_db() -> Dict[str, MonsterSpec]:
    ensure_default_monsters_file()
    with open(MONSTER_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    specs: Dict[str, MonsterSpec] = {}
    for key, d in data.get("monsters", {}).items():
        learnset = [Move(m["name"], int(m["power"]), float(m["accuracy"])) for m in d.get("learnset", [])]
        specs[key] = MonsterSpec(
            key=key,
            name=d["name"],
            element=d["element"],
            base_hp=int(d["base_hp"]),
            base_atk=int(d["base_atk"]),
            base_def=int(d["base_def"]),
            base_spd=int(d["base_spd"]),
            catch_rate=int(d.get("catch_rate", 100)),
            icon=d.get("icon"),
            learnset=learnset,
        )
    return specs

# ------------------ Battle math ------------------

def type_multiplier(attacker: Monster, defender: Monster) -> float:
    return ELEMENT_EFFECTIVENESS.get((attacker.spec.element, defender.spec.element), 1.0)


def calc_damage(attacker: Monster, defender: Monster, move: Move) -> Tuple[int, str]:
    import random as _r
    if _r.random() > move.accuracy:
        return 0, f"{attacker.spec.name}'s {move.name} missed!"
    base = move.power + attacker.atk - defender.defense
    base = max(1, base)
    mult = type_multiplier(attacker, defender)
    variance = _r.uniform(0.85, 1.0)
    dmg = int(base * mult * variance)
    note = ""
    if mult > 1.0:
        note = " It's super effective!"
    elif mult < 1.0:
        note = " It's not very effective."
    return dmg, f"{attacker.spec.name} used {move.name}!{note}"


def attempt_capture(target: Monster, ball_bonus: float = 1.0) -> bool:
    catch_rate = target.spec.catch_rate
    a = (catch_rate * ball_bonus) / (255 / 3)
    p = min(0.95, max(0.05, 0.2 + a * 0.15))
    import random as _r
    return _r.random() < p

# ------------------ Tkinter App ------------------

import tkinter as tk
from tkinter import messagebox, ttk

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Monster Collector — Tkinter Edition")
        self.resizable(False, False)
        os.makedirs(os.path.join(ASSETS_DIR, "monsters"), exist_ok=True)

        # Game state
        self.specs = load_monster_db()
        self.player = Player()
        starter_key = random.choice(list(self.specs.keys()))
        self.player.party.append(Monster(self.specs[starter_key], level=3))

        # UI frames
        self.map_canvas = tk.Canvas(self, width=CANVAS_W, height=CANVAS_H, bg="#1a1a1a", highlightthickness=0)
        self.map_canvas.grid(row=0, column=0, padx=8, pady=8)

        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=1, sticky="ns", padx=(0,8), pady=8)

        self.battle_frame = BattleFrame(self)
        self.battle_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(0,8))

        self.bind_all("<Key>", self.on_key)
        self.redraw_map()
        self.update_sidebar()

    # ------------- Rendering -------------
    def redraw_map(self):
        c = self.map_canvas
        c.delete("all")
        for y, row in enumerate(WORLD_MAP):
            for x, ch in enumerate(row):
                x0, y0 = x * TILE, y * TILE
                x1, y1 = x0 + TILE, y0 + TILE
                if ch == '#':
                    c.create_rectangle(x0, y0, x1, y1, fill="#3a3a3a", outline="#2a2a2a")
                elif ch == 'T':
                    c.create_rectangle(x0, y0, x1, y1, fill="#2f5d34", outline="#244a29")
                    c.create_line(x0+6, y1-6, x1-6, y0+6, fill="#26572b")
                elif ch == 'H':
                    c.create_rectangle(x0, y0, x1, y1, fill="#2c3e50", outline="#1f2d3a")
                    c.create_text((x0+x1)//2, (y0+y1)//2, text='H', fill='white')
                elif ch == 'C':
                    c.create_rectangle(x0, y0, x1, y1, fill="#6d4c41", outline="#4e382f")
                    c.create_text((x0+x1)//2, (y0+y1)//2, text='C', fill='white')
                else:  # '.', ' ', etc.
                    c.create_rectangle(x0, y0, x1, y1, fill="#2b2b2b", outline="#222")
        # draw player
        px, py = self.player.x, self.player.y
        c.create_oval(px*TILE+6, py*TILE+6, px*TILE+TILE-6, py*TILE+TILE-6, fill="#cddc39", outline="#9e9d24")

    def tile_at(self, x: int, y: int) -> str:
        if 0 <= y < len(WORLD_MAP) and 0 <= x < len(WORLD_MAP[0]):
            return WORLD_MAP[y][x]
        return '#'

    def update_sidebar(self):
        self.sidebar.refresh(self.player)

    # ------------- Input -------------
    def on_key(self, ev):
        if self.battle_frame.active:
            # battle consumes inputs
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

            # random encounters on walkable terrain
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
        wild = self.random_wild()
        if not self.player.party:
            return
        self.battle_frame.start(self.player, wild)

    def random_wild(self) -> Monster:
        key = random.choice(list(self.specs.keys()))
        spec = self.specs[key]
        lvl = random.randint(2, 6)
        return Monster(spec=spec, level=lvl)

    def heal_party(self):
        # current HP tracked only during battle; out of battle everyone is considered healthy
        pass

# ------------------ Sidebar ------------------

class Sidebar(tk.Frame):
    def __init__(self, master: GameApp):
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

    def refresh(self, player: 'Player'):
        self.money_var.set(f"Money: {player.money} — Bag: " + ", ".join(f"{k}x{v}" for k,v in player.bag.items()))
        if player.active():
            a = player.active()
            self.active_var.set(f"Active: {a.spec.name} Lv{a.level} [{a.spec.element}]\nHP {a.max_hp}")
        else:
            self.active_var.set("No active monster.")

    def open_bag(self):
        BagDialog(self, self.master.player)

    def open_party(self):
        PartyDialog(self, self.master.player)

    def open_catalog(self):
        CatalogDialog(self, self.master.specs)

# ------------------ Battle Frame ------------------

class BattleFrame(tk.Frame):
    def __init__(self, master: GameApp):
        super().__init__(master, relief="ridge", borderwidth=1)
        self.active = False
        self.player = None
        self.pl = None
        self.en = None
        self.msg_var = tk.StringVar(value="")

        top = tk.Frame(self)
        top.pack(fill="x", padx=6, pady=4)
        self.you_var = tk.StringVar()
        self.foe_var = tk.StringVar()
        tk.Label(top, textvariable=self.you_var, anchor="w").pack(side="left", expand=True, fill="x")
        tk.Label(top, textvariable=self.foe_var, anchor="e").pack(side="right", expand=True, fill="x")

        self.msg = tk.Label(self, textvariable=self.msg_var, anchor="w", justify="left")
        self.msg.pack(fill="x", padx=6)

        btns = tk.Frame(self)
        btns.pack(fill="x", padx=6, pady=6)
        self.btn_move1 = ttk.Button(btns, text="Move1", command=lambda: self.turn(1))
        self.btn_move2 = ttk.Button(btns, text="Move2", command=lambda: self.turn(2))
        self.btn_bag = ttk.Button(btns, text="Bag", command=self.use_bag)
        self.btn_run = ttk.Button(btns, text="Run", command=self.try_run)
        for b in (self.btn_move1, self.btn_move2, self.btn_bag, self.btn_run):
            b.pack(side="left", expand=True, fill="x", padx=2)

    def start(self, player: 'Player', wild: Monster):
        self.player = player
        self.pl = Combatant(player.active(), player.active().max_hp)
        self.en = Combatant(wild, wild.max_hp)
        self.active = True
        self.pack_forget(); self.grid()
        self.refresh()
        self.msg_var.set(f"A wild {wild.spec.name} Lv{wild.level} appeared!")

    def end(self):
        self.active = False
        self.msg_var.set("")
        self.grid()
        self.master.update_sidebar()

    def refresh(self):
        self.you_var.set(f"You: {self.pl.mon.spec.name} HP {self.pl.current_hp}/{self.pl.mon.max_hp}")
        self.foe_var.set(f"Wild: {self.en.mon.spec.name} HP {self.en.current_hp}/{self.en.mon.max_hp}")
        self.btn_move1.configure(text=self.pl.mon.moves[0].name if self.pl.mon.moves else "Move1")
        if len(self.pl.mon.moves) > 1:
            self.btn_move2.configure(text=self.pl.mon.moves[1].name)
        else:
            self.btn_move2.configure(text="—", state="disabled")

    def turn(self, move_idx: int):
        if not self.active:
            return
        # determine order
        player_first = self.pl.mon.speed >= self.en.mon.speed
        order = [("player", move_idx), ("enemy", None)] if player_first else [("enemy", None), ("player", move_idx)]
        log = []
        for who, idx in order:
            if self.pl.current_hp <= 0 or self.en.current_hp <= 0:
                break
            if who == "player":
                mv = self.pl.mon.moves[min(max(idx-1,0), len(self.pl.mon.moves)-1)]
                dmg, msg = calc_damage(self.pl.mon, self.en.mon, mv)
                self.en.current_hp = max(0, self.en.current_hp - dmg)
                log.append(msg)
            else:
                mv = random.choice(self.en.mon.moves)
                dmg, msg = calc_damage(self.en.mon, self.pl.mon, mv)
                self.pl.current_hp = max(0, self.pl.current_hp - dmg)
                log.append(msg)
        self.msg_var.set("\n".join(log))
        self.refresh()
        self.after(50, self.check_outcome)

    def check_outcome(self):
        if self.en.current_hp <= 0:
            logs = self.pl.mon.gain_exp(12 + self.en.mon.level * 3)
            messagebox.showinfo("Battle", "The wild fainted!\n" + "\n".join(logs))
            self.end()
        elif self.pl.current_hp <= 0:
            # Player's active monster fainted. Do NOT remove from party.
            # If this was the last standing monster, send player back to the hut and fully heal.
            if len(self.player.party) <= 1:
                messagebox.showinfo("Battle", f"{self.pl.mon.spec.name} fainted! You blacked out and returned to the hut.")
                self.master.heal_party()
                self.master.player.x, self.master.player.y = 1, 1
                self.master.redraw_map()
            else:
                messagebox.showinfo("Battle", f"{self.pl.mon.spec.name} fainted! You lost the battle.")
            self.end()

    def use_bag(self):
        if not self.active:
            return
        # Simple bag actions inside battle
        items = list(self.player.bag.items())
        if not items:
            messagebox.showinfo("Bag", "Your bag is empty.")
            return
        BagUseDialog(self, self.player, on_use=self.after_bag_action)

    def after_bag_action(self, did_action: bool, used_capture: bool):
        if not did_action:
            return
        if used_capture:
            if attempt_capture(self.en.mon, ball_bonus=1.2):
                messagebox.showinfo("Capture", f"Gotcha! {self.en.mon.spec.name} was captured!")
                self.player.party.append(self.en.mon)
                self.end()
                return
            else:
                self.msg_var.set(f"The wild {self.en.mon.spec.name} broke free!")
                # enemy gets a free move
                mv = random.choice(self.en.mon.moves)
                dmg, msg = calc_damage(self.en.mon, self.pl.mon, mv)
                self.pl.current_hp = max(0, self.pl.current_hp - dmg)
                self.refresh()
                self.after(50, self.check_outcome)
        else:
            # enemy acts once after your bag use
            mv = random.choice(self.en.mon.moves)
            dmg, msg = calc_damage(self.en.mon, self.pl.mon, mv)
            self.pl.current_hp = max(0, self.pl.current_hp - dmg)
            self.msg_var.set(msg)
            self.refresh()
            self.after(50, self.check_outcome)

    def try_run(self):
        import random as _r
        if _r.random() < 0.6 or self.pl.mon.speed >= self.en.mon.speed:
            messagebox.showinfo("Run", "You fled successfully!")
            self.end()
        else:
            messagebox.showinfo("Run", "Couldn't escape!")
            # enemy free move
            mv = random.choice(self.en.mon.moves)
            dmg, msg = calc_damage(self.en.mon, self.pl.mon, mv)
            self.pl.current_hp = max(0, self.pl.current_hp - dmg)
            self.msg_var.set(msg)
            self.refresh()
            self.after(50, self.check_outcome)

# ------------------ Dialogs ------------------

class BagDialog(tk.Toplevel):
    def __init__(self, master, player: 'Player'):
        super().__init__(master)
        self.title("Bag")
        self.resizable(False, False)
        self.player = player
        frm = tk.Frame(self); frm.pack(padx=10, pady=10)
        for item, qty in player.bag.items():
            tk.Label(frm, text=f"{item}: x{qty}").pack(anchor="w")
        ttk.Button(frm, text="Close", command=self.destroy).pack(pady=(8,0))

class BagUseDialog(tk.Toplevel):
    def __init__(self, master: BattleFrame, player: 'Player', on_use):
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
            # heal active
            bf: BattleFrame = self.master
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

class PartyDialog(tk.Toplevel):
    def __init__(self, master, player: 'Player'):
        super().__init__(master)
        self.title("Party")
        self.resizable(False, False)
        self.player = player
        self.list = tk.Listbox(self, width=28)
        self.list.pack(side="left", fill="both", expand=True, padx=(8,0), pady=8)
        btns = tk.Frame(self); btns.pack(side="right", fill="y", padx=8, pady=8)
        ttk.Button(btns, text="View Icon", command=self.view_icon).pack(fill="x", pady=2)
        ttk.Button(btns, text="Make Lead", command=self.make_lead).pack(fill="x", pady=2)
        ttk.Button(btns, text="Release", command=self.release).pack(fill="x", pady=2)
        ttk.Button(btns, text="Close", command=self.destroy).pack(fill="x", pady=(8,2))
        self.refresh()

    def refresh(self):
        self.list.delete(0, tk.END)
        for m in self.player.party:
            self.list.insert(tk.END, f"{m.spec.name} Lv{m.level} ({m.spec.element})")

    def selected(self) -> Optional[int]:
        sel = self.list.curselection()
        return sel[0] if sel else None

    def view_icon(self):
        idx = self.selected()
        if idx is None: return
        m = self.player.party[idx]
        IconViewer(self, m)

    def make_lead(self):
        idx = self.selected()
        if idx is None or idx == 0: return
        self.player.party[0], self.player.party[idx] = self.player.party[idx], self.player.party[0]
        self.refresh()
        self.master.update_sidebar()

    def release(self):
        idx = self.selected()
        if idx is None: return
        m = self.player.party.pop(idx)
        messagebox.showinfo("Release", f"Released {m.spec.name}.")
        self.refresh()
        self.master.update_sidebar()

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
        # Load PNG/GIF via PhotoImage; show placeholder if not found
        img = None
        if mon.spec.icon and os.path.exists(mon.spec.icon):
            try:
                img = tk.PhotoImage(file=mon.spec.icon)
            except Exception as e:
                img = None
        if img is None:
            # placeholder canvas
            cv = tk.Canvas(self, width=128, height=128, bg="#222", highlightthickness=0)
            cv.pack(padx=10, pady=10)
            cv.create_rectangle(8,8,120,120, outline="#666")
            cv.create_text(64,64, text=mon.spec.name, fill="#aaa", width=110)
        else:
            # scale down to max 128x128 if larger
            w,h = img.width(), img.height()
            maxd = 128
            # integer subsample only; keeps it simple and crisp for pixel art
            ss = max(1, max(w//maxd, h//maxd))
            if ss > 1:
                img = img.subsample(ss, ss)
            lbl = tk.Label(self, image=img)
            lbl.image = img  # keep ref
            lbl.pack(padx=8, pady=8)
        tk.Label(self, text=f"{mon.spec.name} (Lv {mon.level}) — {mon.spec.element}").pack(pady=(0,8))
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=(0,8))

class ShopDialog(tk.Toplevel):
    def __init__(self, master, player: 'Player'):
        super().__init__(master)
        self.title("Charm Shop")
        self.resizable(False, False)
        self.player = player
        frm = tk.Frame(self); frm.pack(padx=12, pady=12)
        tk.Label(frm, text=f"Coins: {player.money}").pack(anchor="w")
        ttk.Button(frm, text="Buy Charm Orb (50)", command=self.buy_orb).pack(fill="x", pady=2)
        ttk.Button(frm, text="Buy Potion (40)", command=self.buy_potion).pack(fill="x", pady=2)
        ttk.Button(frm, text="Close", command=self.destroy).pack(fill="x", pady=(8,0))

    def buy_orb(self):
        if self.player.money >= 50:
            self.player.money -= 50
            self.player.bag["Charm Orb"] = self.player.bag.get("Charm Orb", 0) + 1
            self.master.update_sidebar()
        else:
            messagebox.showinfo("Shop", "Not enough coins.")

    def buy_potion(self):
        if self.player.money >= 40:
            self.player.money -= 40
            self.player.bag["Potion"] = self.player.bag.get("Potion", 0) + 1
            self.master.update_sidebar()
        else:
            messagebox.showinfo("Shop", "Not enough coins.")

# ------------------ Combatant & Player ------------------

@dataclass
class Combatant:
    mon: Monster
    current_hp: int

@dataclass
class Player:
    x: int = 1
    y: int = 1
    party: List[Monster] = field(default_factory=list)
    bag: Dict[str, int] = field(default_factory=lambda: {"Charm Orb": 3, "Potion": 2})
    money: int = 200

    def active(self) -> Optional[Monster]:
        return self.party[0] if self.party else None

# ------------------ Main ------------------

def main():
    try:
        app = GameApp()
        app.mainloop()
    except tk.TclError as e:
        print("Tkinter error:", e)
        print("If you're missing Tk, see installation tips: \n- Ubuntu/Debian: sudo apt install python3-tk\n- Fedora: sudo dnf install python3-tkinter\n- macOS (brew): brew install python-tk")

if __name__ == "__main__":
    main()
