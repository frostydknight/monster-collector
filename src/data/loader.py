import os
import json
from models.monster import Move, MonsterSpec
from models.constants import ASSETS_DIR, MONSTER_JSON

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
        "base_atk": 8,
        "base_def": 12,
        "base_spd": 6,
        "catch_rate": 120,
        "icon": "assets/monsters/minotaur.png",
        "learnset": [
            {"name": "Tackle", "power": 30, "accuracy": 0.95},
            {"name": "Labyrinth Rush", "power": 40, "accuracy": 0.85},
        ],
    },
    "caterpillar_girl": {
        "name": "Caterpillar Girl",
        "element": "Normal",
        "base_hp": 20,
        "base_atk": 8,
        "base_def": 8,
        "base_spd": 8,
        "catch_rate": 180,
        "icon": "assets/monsters/caterpillar_girl.png",
        "learnset": [
            {"name": "Tackle", "power": 30, "accuracy": 0.95},
            {"name": "String Shot", "power": 20, "accuracy": 1.0},
        ],
    },
    "mouse_girl": {
        "name": "Mouse Girl",
        "element": "Normal",
        "base_hp": 16,
        "base_atk": 7,
        "base_def": 5,
        "base_spd": 14,
        "catch_rate": 200,
        "icon": "assets/monsters/mouse_girl.png",
        "learnset": [
            {"name": "Tackle", "power": 30, "accuracy": 0.95},
            {"name": "Dart", "power": 20, "accuracy": 1.0},
        ],
    },
}

def ensure_default_monsters_file():
    if not os.path.exists(MONSTER_JSON):
        os.makedirs(os.path.dirname(MONSTER_JSON), exist_ok=True)
        with open(MONSTER_JSON, "w", encoding="utf-8") as f:
            json.dump({"monsters": DEFAULT_MONSTERS}, f, indent=2)

def load_monster_db() -> dict:
    ensure_default_monsters_file()
    with open(MONSTER_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    specs = {}
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
            evolves_to=d.get("evolves_to"),
            evolution_level = int(d["evolution_level"]) if str(d.get("evolution_level", "")).isdigit() else None,
            evolution_requirements=d.get("evolution_requirements", {}),
        )
    return specs
