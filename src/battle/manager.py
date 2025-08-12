from models.monster import Monster
import random

class BattleManager:
    @staticmethod
    def start_wild_battle(game_app):
        wild = BattleManager.random_wild(game_app)
        if not game_app.player.party:
            return
        if not game_app.in_battle:
            game_app.in_battle = True
            from battle.battle_window import BattleWindow
            BattleWindow(game_app, game_app.player, enemy_party=[wild], is_trainer=False)

    @staticmethod
    def random_wild(game_app) -> Monster:
        key = random.choice(list(game_app.specs.keys()))
        spec = game_app.specs[key]
        lvl = random.randint(2, 4)
        return Monster(spec=spec, level=lvl)

    @staticmethod
    def heal_party(game_app):
        # current HP tracked only during battle; out of battle everyone is considered healthy
        pass
