# Monster Collector — Tkinter Edition

A simple monster-collecting RPG built with Python and Tkinter. Explore the overworld, battle wild monsters and trainers, collect and manage your party, and shop for items. No external dependencies beyond the Python standard library.

## Project Structure

```
Mon-Collector/
│
├── src/
│   ├── main.py                  # Entry point, launches the app
│   │
│   ├── core/
│   │   ├── game_controller.py   # GameApp class and main game logic
│   │   └── map_manager.py       # TileIconManager and map/tile rendering logic
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── monster.py           # Monster, MonsterSpec, Move, Combatant classes
│   │   ├── player.py            # Player class
│   │   ├── trainer.py           # Trainer class and helpers
│   │   └── constants.py         # WORLD_MAP, ELEMENT_EFFECTIVENESS, asset/data paths, etc.
│   │
│   ├── battle/
│   │   ├── __init__.py
│   │   ├── battle_window.py     # BattleWindow class and related logic
│   │   ├── damage.py            # calc_damage, type_multiplier, attempt_capture
│   │   ├── dialogs.py           # SwitchDialog, BagDialog, BagUseDialog, etc.
│   │   └── manager.py           # BattleManager for battle logic
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── sidebar.py           # Sidebar class
│   │   ├── catalog.py           # CatalogDialog, IconViewer
│   │   ├── party.py             # PartyDialog and party UI
│   │   └── shop.py              # ShopDialog
│   │
│   ├── data/
│   │   ├── loader.py            # Data loading and default monster setup
│   │   └── monsters.json        # Monster data
│   │
│   └── assets/
│       └── monsters/            # Monster images
│       └── tiles/               # Tile images
│
└── README.md                    # Project documentation
```

## Code Documentation

### main.py
- Entry point for the game. Instantiates and runs the `GameApp` from `core/game_controller.py`.

### core/game_controller.py
- Contains the `GameApp` class, which manages the main window, game state, player movement, event handling, and UI updates.

### core/map_manager.py
- Handles tile and map rendering, including the `TileIconManager` for loading and scaling tile images.

### models/
- `monster.py`: Defines monster data structures and logic.
- `player.py`: Player data and party management.
- `trainer.py`: Trainer data and engagement logic.
- `constants.py`: Game constants, world map, and centralized asset/data paths.

### battle/
- `battle_window.py`: Battle UI and turn logic.
- `damage.py`: Damage calculation and type effectiveness.
- `dialogs.py`: Battle-related dialogs (switch, bag, etc.).
- `manager.py`: Centralized battle logic (e.g., wild battle initiation).

### ui/
- `sidebar.py`: Sidebar UI for player info.
- `catalog.py`: Monster catalog and icon viewer.
- `party.py`: Party management UI.
- `shop.py`: Shop dialog and item purchasing.

### data/
- `loader.py`: Loads monster data and ensures default data exists.
- `monsters.json`: Monster definitions and learnsets.

### assets/
- `monsters/`: Monster sprite images.
- `tiles/`: Tile images for the overworld map.

---

## Getting Started

1. Make sure you have Python 3.x installed with Tkinter support.
2. Run the game:
   ```sh
   python src/main.py
   ```
3. Controls:
   - Move: WASD or arrow keys
   - I: Bag, P: Party, C: Catalog, H: Help
   - Step on H (hut) to heal, C (shop) to open shop

---

## License
MIT