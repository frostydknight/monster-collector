from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .monster import Monster

@dataclass
class Player:
    x: int = 1
    y: int = 1
    party: List[Monster] = field(default_factory=list)
    bag: Dict[str, int] = field(default_factory=lambda: {"Charm Orb": 3, "Potion": 2})
    money: int = 200

    def active(self) -> Optional[Monster]:
        return self.party[0] if self.party else None

    def add_to_party(self, monster):
        """Add a monster to the party if there is space. Returns True if added, False if full."""
        if len(self.party) < 6:
            self.party.append(monster)
            return True
        return False
