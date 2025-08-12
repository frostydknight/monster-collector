Mon-Collector/
│
├── main.py                  # Entry point, launches the app
├── models/
│   ├── __init__.py
│   ├── monster.py           # Monster, MonsterSpec, Move, Combatant classes
│   ├── player.py            # Player class
│   ├── trainer.py           # Trainer class
│   └── constants.py         # WORLD_MAP, ELEMENT_EFFECTIVENESS, etc.
│
├── battle/
│   ├── __init__.py
│   ├── battle_window.py     # BattleWindow class and related logic
│   ├── damage.py            # calc_damage, type_multiplier, attempt_capture
│   └── dialogs.py           # SwitchDialog, BagDialog, BagUseDialog, etc.
│
├── ui/
│   ├── __init__.py
│   ├── sidebar.py           # Sidebar class
│   ├── catalog.py           # CatalogDialog, IconViewer
│   └── shop.py              # ShopDialog
│
├── data/
│   └── monsters.json        # Monster data
│
├── assets/
│   └── monsters/            # Monster images
│
└── utils/
    ├── __init__.py
    └── file_utils.py        # File loading/saving helpers