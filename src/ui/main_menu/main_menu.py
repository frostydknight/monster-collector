import tkinter as tk
from tkinter import simpledialog, messagebox
from models.constants import SAVE_DIR
import os
import json


os.makedirs(SAVE_DIR, exist_ok=True)

class MainMenu(tk.Toplevel):
    def __init__(self, master, on_profile_loaded):
        super().__init__(master)
        self.title("Main Menu")
        self.on_profile_loaded = on_profile_loaded
        self.geometry("300x200")
        self.resizable(False, False)

        tk.Label(self, text="Monster Collector", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Button(self, text="New Profile", width=20, command=self.create_profile).pack(pady=5)
        tk.Button(self, text="Load Profile", width=20, command=self.load_profile).pack(pady=5)
        tk.Button(self, text="Quit", width=20, command=self.quit_game).pack(pady=5)

    def create_profile(self):
        name = simpledialog.askstring("New Profile", "Enter your name:", parent=self)
        if not name:
            return
        save_path = os.path.join(SAVE_DIR, f"{name}.json")
        if os.path.exists(save_path):
            messagebox.showerror("Error", "Profile already exists!")
            return
        profile = {"name": name, "data": {}}
        with open(save_path, 'w') as f:
            json.dump(profile, f)
        self.on_profile_loaded(profile)
        self.destroy()

    def load_profile(self):
        profiles = [f[:-5] for f in os.listdir(SAVE_DIR) if f.endswith('.json')]
        if not profiles:
            messagebox.showinfo("No Profiles", "No profiles found. Create a new one!")
            return
        name = simpledialog.askstring("Load Profile", f"Available: {', '.join(profiles)}\nEnter profile name:", parent=self)
        if not name:
            return
        save_path = os.path.join(SAVE_DIR, f"{name}.json")
        if not os.path.exists(save_path):
            messagebox.showerror("Error", "Profile not found!")
            return
        with open(save_path) as f:
            profile = json.load(f)
        self.on_profile_loaded(profile)
        self.destroy()

    def quit_game(self):
        self.master.destroy()
