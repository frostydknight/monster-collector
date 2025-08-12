import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Optional
from models.monster import Monster, Combatant
from models.player import Player
from models.trainer import Trainer
from battle.dialogs import SwitchDialog, BagDialog, BagUseDialog
from battle.damage import calc_damage, attempt_capture
from models.constants import ASSETS_DIR
import os

class BattleWindow(tk.Toplevel):
    def __init__(self, app, player: Player,
                 enemy_party: Optional[List[Monster]] = None,
                 is_trainer: bool = False,
                 trainer_ref=None,
                 on_trainer_defeated=None):
        super().__init__(app)
        self.app = app
        self.player = player
        self.title("Battle")
        self.resizable(False, False)
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.transient(app)
        self.grab_set()

        self.party_state: List[Combatant] = [Combatant(m, m.max_hp) for m in player.party]
        self.pl_index: int = 0
        self.pl: Combatant = self.party_state[self.pl_index]
        self.is_trainer = is_trainer
        self.trainer_ref = trainer_ref
        self.on_trainer_defeated_cb = on_trainer_defeated

        if enemy_party is None:
            enemy_party = []
        elif isinstance(enemy_party, Monster):
            enemy_party = [enemy_party]

        if enemy_party and len(enemy_party) > 0:
            self.enemy_party_state: List[Combatant] = [Combatant(m, m.max_hp) for m in enemy_party]
            self.en_index = 0
            self.en = self.enemy_party_state[self.en_index]
            self.msg_var = tk.StringVar(value=f"Trainer challenges you with {self.en.mon.spec.name} Lv{self.en.mon.level}!")
        else:
            wild = self.app.random_wild()
            self.enemy_party_state = [Combatant(wild, wild.max_hp)]
            self.en_index = 0
            self.en = self.enemy_party_state[0]
            self.msg_var = tk.StringVar(value=f"A wild {wild.spec.name} Lv{wild.level} appeared!")

        main = tk.Frame(self, bg="#1b1b1b")
        main.pack(padx=20, pady=20, fill="both", expand=True)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

        self.foe_var = tk.StringVar()
        foe_box = tk.Frame(main, bg="#263238", bd=2, relief="ridge")
        foe_box.grid(row=0, column=0, sticky="nw", padx=12, pady=12)
        tk.Label(foe_box, textvariable=self.foe_var, fg="white", bg="#263238", 
                 justify="left", padx=12, pady=10, font=("TkDefaultFont", 12, "bold")).pack()

        self.foe_img_label = tk.Label(main, bg="#1b1b1b")
        self.foe_img_label.grid(row=0, column=1, sticky="ne", padx=12, pady=12)

        self.you_var = tk.StringVar()
        you_box = tk.Frame(main, bg="#263238", bd=2, relief="ridge")
        you_box.grid(row=1, column=0, sticky="sw", padx=12, pady=12)
        tk.Label(you_box, textvariable=self.you_var, fg="white", bg="#263238", 
                 justify="left", padx=12, pady=10, font=("TkDefaultFont", 12, "bold")).pack()

        right_col = tk.Frame(main, bg="#1b1b1b")
        right_col.grid(row=1, column=1, sticky="se", padx=12, pady=12)
        self.you_img_label = tk.Label(right_col, bg="#1b1b1b")
        self.you_img_label.pack(anchor="e", pady=(0,12))

        msg_box = tk.Frame(self, bg="#111")
        msg_box.pack(fill="x", padx=20, pady=(0,10))
        tk.Label(msg_box, textvariable=self.msg_var, fg="white", bg="#111", anchor="w", 
                 justify="left", padx=12, pady=8, font=("TkDefaultFont", 11)).pack(fill="x")

        cmd_box = tk.Frame(right_col)
        cmd_box.pack(anchor="e", pady=10)
        self.btn_move1 = ttk.Button(cmd_box, text="Move1", command=lambda: self.turn(1), width=18)
        self.btn_move2 = ttk.Button(cmd_box, text="Move2", command=lambda: self.turn(2), width=18)
        self.btn_bag   = ttk.Button(cmd_box, text="Bag",   command=self.use_bag, width=18)
        self.btn_switch= ttk.Button(cmd_box, text="Switch", command=self.open_switch_dialog, width=18)
        self.btn_run   = ttk.Button(cmd_box, text="Run",   command=self.try_run, width=18)
        for b in (self.btn_move1, self.btn_move2, self.btn_bag, self.btn_switch, self.btn_run):
            b.pack(fill="x", pady=4)

        self.set_icon(self.foe_img_label, self.en.mon, maxd=160)
        self.set_icon(self.you_img_label, self.pl.mon, maxd=160)

        self.refresh()

    def on_close(self):
        # Prevent closing the battle window via the window manager (X button)
        pass

    def use_bag(self):
        # Open the BagUseDialog and handle the result in after_bag_action
        BagUseDialog(self, self.player, on_use=self.after_bag_action)

    def after_bag_action(self, did_action: bool, used_capture: bool):
        if not did_action:
            return
        if used_capture:
            if self.is_trainer:
                messagebox.showinfo("Capture", "You can't capture a trainer's monster!")
                self.player.bag["Charm Orb"] = self.player.bag.get("Charm Orb", 0) + 1
                return
            if attempt_capture(self.en.mon, ball_bonus=1.2):
                messagebox.showinfo("Capture", f"Gotcha! {self.en.mon.spec.name} was captured!")
                if self.player.add_to_party(self.en.mon):
                    messagebox.showinfo("Capture", f"Gotcha! {self.en.mon.spec.name} was captured and added to your party!")
                    self.end()
                    return
                else:
                    messagebox.showinfo("Capture", f"Your party is full (6). {self.en.mon.spec.name} fled!")
                    self.end()
                    return
            else:
                self.msg_var.set(f"The wild {self.en.mon.spec.name} broke free!")
                import random
                mv = random.choice(self.en.mon.moves)
                dmg, msg = calc_damage(self.en.mon, self.pl.mon, mv)
                self.pl.current_hp = max(0, self.pl.current_hp - dmg)
                self.refresh(); self.after(50, self.check_outcome)
        else:
            import random
            mv = random.choice(self.en.mon.moves)
            dmg, msg = calc_damage(self.en.mon, self.pl.mon, mv)
            self.pl.current_hp = max(0, self.pl.current_hp - dmg)
            self.msg_var.set(msg)
            self.refresh(); self.after(50, self.check_outcome)

    def open_switch_dialog(self, force: bool = False):
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        dlg_master = self
        try:
            SwitchDialog(
                dlg_master,
                self.party_state,
                self.pl_index,
                on_switch=lambda i: self.switch_to(i, enemy_free=not force)
            )
        except tk.TclError:
            return

    def try_run(self):
        import random
        if random.random() < 0.6 or self.pl.mon.speed >= self.en.mon.speed:
            messagebox.showinfo("Run", "You fled successfully!")
            self.end()
        else:
            messagebox.showinfo("Run", "Couldn't escape!")
            mv = random.choice(self.en.mon.moves)
            dmg, msg = calc_damage(self.en.mon, self.pl.mon, mv)
            self.pl.current_hp = max(0, self.pl.current_hp - dmg)
            self.msg_var.set(msg)
            self.refresh(); self.after(50, self.check_outcome)

    def set_icon(self, label: tk.Label, mon: Monster, maxd: int = 128):
        img = None
        icon_path = mon.spec.icon
        if icon_path and not os.path.isabs(icon_path):
            if icon_path.startswith("assets/"):
                rel_path = icon_path[len("assets/"):]
                icon_path = os.path.join(ASSETS_DIR, rel_path)
            else:
                icon_path = os.path.join(ASSETS_DIR, icon_path)
        if icon_path and os.path.exists(icon_path):
            try:
                raw = tk.PhotoImage(file=icon_path)
                w, h = raw.width(), raw.height()
                ss = max(1, max(w // maxd, h // maxd))
                img = raw.subsample(ss, ss) if ss > 1 else raw
            except Exception:
                img = None
        if img is None:
            label.configure(text=mon.spec.name, image="", fg="#ccc", bg="#1b1b1b")
            label.image = None
        else:
            label.configure(image=img, text="")
            label.image = img

    def refresh(self):
        self.you_var.set(f"{self.pl.mon.spec.name}  Lv{self.pl.mon.level}\nHP {self.pl.current_hp}/{self.pl.mon.max_hp}")
        self.foe_var.set(f"{self.en.mon.spec.name}  Lv{self.en.mon.level}\nHP {self.en.current_hp}/{self.en.mon.max_hp}")
        self.btn_move1.configure(text=self.pl.mon.moves[0].name if self.pl.mon.moves else "Move1")
        if len(self.pl.mon.moves) > 1:
            self.btn_move2.configure(text=self.pl.mon.moves[1].name, state="normal")
        else:
            self.btn_move2.configure(text="—", state="disabled")
        if hasattr(self, "btn_switch"):
            self.btn_switch.configure(state=("normal" if len(self.alive_indices()) > 1 else "disabled"))

    def switch_to(self, new_idx: int, enemy_free: bool = True):
        if new_idx == self.pl_index:
            return
        if self.party_state[new_idx].current_hp <= 0:
            return
        self.pl_index = new_idx
        self.pl = self.party_state[self.pl_index]
        self.set_icon(self.you_img_label, self.pl.mon, maxd=160)
        self.refresh()
        if enemy_free and self.en.current_hp > 0:
            import random
            mv = random.choice(self.en.mon.moves)
            dmg, msg = calc_damage(self.en.mon, self.pl.mon, mv)
            self.pl.current_hp = max(0, self.pl.current_hp - dmg)
            self.msg_var.set("Switched!\n" + msg)
            self.after(50, self.check_outcome)
        else:
            self.msg_var.set("Switched!")

    def alive_indices(self) -> list:
        return [i for i, c in enumerate(self.party_state) if c.current_hp > 0]

    def check_outcome(self):
        if self.en.current_hp <= 0:
            logs = self.pl.mon.gain_exp(12 + self.en.mon.level * 3)
            # Evolution check after gaining EXP and possibly leveling up
            from data.loader import load_monster_db
            monster_db = load_monster_db()
            if self.pl.mon.can_evolve():
                old_name = self.pl.mon.spec.name
                self.pl.mon.evolve(monster_db)
                logs.append(f"{old_name} evolved into {self.pl.mon.spec.name}!")
            if self.is_trainer and self.en_index + 1 < len(self.enemy_party_state):
                self.en_index += 1
                self.en = self.enemy_party_state[self.en_index]
                self.set_icon(self.foe_img_label, self.en.mon, maxd=160)
                self.refresh()
                messagebox.showinfo("Battle", "Foe fainted!\n" + "\n".join(logs) +
                                    f"\nTrainer sends out {self.en.mon.spec.name} Lv{self.en.mon.level}!")
                return
            else:
                if self.is_trainer:
                    messagebox.showinfo("Battle", "Trainer is out of monsters!\n" + "\n".join(logs))
                    if self.on_trainer_defeated_cb and self.trainer_ref:
                        self.on_trainer_defeated_cb(self.trainer_ref)
                else:
                    messagebox.showinfo("Battle", "The wild fainted!\n" + "\n".join(logs))
                self.end()
                return
        elif self.pl.current_hp <= 0:
            others = [i for i in self.alive_indices() if i != self.pl_index]
            if others:
                messagebox.showinfo("Battle", f"{self.pl.mon.spec.name} fainted! Choose a replacement.")
                self.open_switch_dialog(force=True)
            else:
                messagebox.showinfo("Battle", f"{self.pl.mon.spec.name} fainted! You blacked out and returned to the hut.")
                self.app.heal_party()
                self.app.player.x, self.app.player.y = 1, 1
                self.app.redraw_map()
                self.end()

    def turn(self, move_idx: int):
        player_first = self.pl.mon.speed >= self.en.mon.speed
        order = [("player", move_idx), ("enemy", None)] if player_first else [("enemy", None), ("player", move_idx)]
        log = []
        for who, idx in order:
            if self.pl.current_hp <= 0 or self.en.current_hp <= 0:
                break
            if who == "player":
                mv = self.pl.mon.moves[min(max(move_idx-1,0), len(self.pl.mon.moves)-1)]
                dmg, msg = calc_damage(self.pl.mon, self.en.mon, mv)
                self.en.current_hp = max(0, self.en.current_hp - dmg)
                log.append(msg)
            else:
                import random
                mv = random.choice(self.en.mon.moves)
                dmg, msg = calc_damage(self.en.mon, self.pl.mon, mv)
                self.pl.current_hp = max(0, self.pl.current_hp - dmg)
                log.append(msg)
        self.msg_var.set("\n".join(log))
        self.refresh()
        self.after(50, self.check_outcome)

    def end(self):
        self.app.in_battle = False
        self.app.update_sidebar()
        self.grab_release()
        self.destroy()