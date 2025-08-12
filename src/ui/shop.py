import tkinter as tk
from tkinter import ttk, messagebox

class ShopDialog(tk.Toplevel):
    def __init__(self, master, player):
        super().__init__(master)
        self.title("Charm Shop")
        self.resizable(False, False)
        self.player = player
        self.master_app = master
        self.PRICES = {
            "Charm Orb": 50,
            "Potion": 40,
        }
        frm = tk.Frame(self)
        frm.pack(padx=12, pady=12)
        self.money_var = tk.StringVar()
        tk.Label(frm, textvariable=self.money_var, font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        tk.Label(frm, text="Items for sale:").pack(anchor="w", pady=(8, 4))
        for item_name, price in self.PRICES.items():
            ttk.Button(
                frm,
                text=f"Buy {item_name} ({price})",
                command=lambda n=item_name, p=price: self.buy_item(n, p)
            ).pack(fill="x", pady=2)
        ttk.Separator(frm, orient="horizontal").pack(fill="x", pady=8)
        ttk.Button(frm, text="Close", command=self.destroy).pack(fill="x")
        self.refresh_money()

    def refresh_money(self):
        self.money_var.set(f"Coins: {self.player.money}  |  Bag: " +
                           ", ".join(f"{k}x{v}" for k, v in self.player.bag.items()) if self.player.bag else f"Coins: {self.player.money}")

    def buy_item(self, name: str, price: int):
        if self.player.money < price:
            messagebox.showinfo("Shop", "Not enough coins.")
            return
        self.player.money -= price
        self.player.bag[name] = self.player.bag.get(name, 0) + 1
        self.refresh_money()
        self.master_app.update_sidebar()
        messagebox.showinfo("Shop", f"Purchased 1x {name}!")
