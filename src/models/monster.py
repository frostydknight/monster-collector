from dataclasses import dataclass, field
from typing import List, Optional

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
    evolves_to: Optional[str] = None
    evolution_level: Optional[int] = None
    evolution_requirements: Optional[dict] = None

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
    
    def can_evolve(self):
        """Check if the monster can evolve based on its spec."""
        return (
            self.spec.evolves_to is not None and
            self.level >= (self.spec.evolution_level or 1000)
        )

    def evolve(self, monster_db):
        if self.can_evolve():
            new_spec = monster_db[self.spec.evolves_to]
            self.spec = new_spec
            # Update moves to the new monster's learnset
            self.moves = [Move(m.name, m.power, m.accuracy) for m in new_spec.learnset]
            # Reset HP to new max
            self.current_hp = self.max_hp

@dataclass
class Combatant:
    mon: Monster
    current_hp: int
