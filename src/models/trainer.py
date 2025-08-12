from dataclasses import dataclass, field
from typing import List, Tuple
from .monster import Monster

@dataclass
class Trainer:
    x: int
    y: int
    facing: str = "S"  # "N", "S", "E", "W"
    defeated: bool = False
    party: List[Monster] = field(default_factory=list)

def create_trainers() -> List[Trainer]:
    coords = [
        (5, 1, "W"),
        (14, 3, "S"),
        (18, 6, "W"),
    ]
    trainers: List[Trainer] = []
    for (tx, ty, face) in coords:
        trainers.append(Trainer(x=tx, y=ty, facing=face))
    return trainers

def tile_in_front_of_trainer(tr: Trainer) -> Tuple[int, int]:
    if tr.facing == "N":
        return tr.x, tr.y - 1
    if tr.facing == "S":
        return tr.x, tr.y + 1
    if tr.facing == "E":
        return tr.x + 1, tr.y
    return tr.x - 1, tr.y

def check_trainer_engagement(game_app):
    if game_app.in_battle:
        return
    for tr in game_app.trainers:
        if tr.defeated:
            continue
        fx, fy = tile_in_front_of_trainer(tr)
        if (game_app.player.x, game_app.player.y) == (fx, fy):
            if not tr.party:
                import random
                keys = list(game_app.specs.keys())
                count = random.randint(1, 2)
                for _ in range(count):
                    spec = game_app.specs[random.choice(keys)]
                    lvl = random.randint(4, 6)
                    tr.party.append(Monster(spec, level=lvl))
            game_app.in_battle = True
            from battle.battle_window import BattleWindow
            BattleWindow(game_app, game_app.player,
                         enemy_party=[m for m in tr.party],
                         is_trainer=True,
                         trainer_ref=tr,
                         on_trainer_defeated=game_app.on_trainer_defeated)
            break

def on_trainer_defeated(game_app, trainer: Trainer):
    trainer.defeated = True
    game_app.player.money += 50
    game_app.update_sidebar()
    game_app.redraw_map()
