# Game constants and data
import os


WORLD_MAP = [
    "########################",
    "#H....TT..####..TT....##",
    "#..####..##..#..#..TT..#",
    "#..#  #..#..##..#..##..#",
    "#..#  #..####..#..###..#",
    "#..#  #..TT....#..#....#",
    "#..####..TTTT..##..###.#",
    "#..T..####..TT..#..T..C#",
    "#..TT..#..#..TT..#..TT.#",
    "#......#....#......#...E#",
    "########################",
]

ELEMENT_EFFECTIVENESS = {
    ("Water", "Fire"): 1.5,
    ("Fire", "Earth"): 1.5,
    ("Earth", "Air"): 1.5,
    ("Air", "Water"): 1.5,
}

TILE = 28
CANVAS_W = len(WORLD_MAP[0]) * TILE
CANVAS_H = len(WORLD_MAP) * TILE

# Asset paths (relative to SRC root)
SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(SRC_ROOT, "assets")
TILE_ICONS_JSON = os.path.join(SRC_ROOT, "data", "tiles.json")
MONSTER_JSON = os.path.join(SRC_ROOT, "data", "monsters.json")

ELEMENT_COLORS = {
    "Water": "#4aa1ff",
    "Fire":  "#ff6b57",
    "Earth": "#a0723a",
    "Air":   "#87d37c",
}

SAVE_DIR = os.path.join(SRC_ROOT, "data", "saves")

# New UI dimensions for 1024x1024 background
MAIN_W = 1024
MAIN_H = 1024
SIDEBAR_W = 224
SIDEBAR_H = MAIN_H
MAP_W = MAIN_W - SIDEBAR_W  # 800
MAP_H = MAIN_H