from typing import Tuple
from models.monster import Monster, Move
from models.constants import ELEMENT_EFFECTIVENESS

def type_multiplier(attacker: Monster, defender: Monster) -> float:
    return ELEMENT_EFFECTIVENESS.get((attacker.spec.element, defender.spec.element), 1.0)

def calc_damage(attacker: Monster, defender: Monster, move: Move) -> Tuple[int, str]:
    """Level-scaled, gentler damage to avoid one-hit KOs."""
    import random as _r
    if _r.random() > move.accuracy:
        return 0, f"{attacker.spec.name}'s {move.name} missed!"
    base = ((0.4 * attacker.level + 2) * move.power * (attacker.atk / max(1, defender.defense))) / 10
    base = max(1.0, base)
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
