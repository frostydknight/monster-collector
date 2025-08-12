#!/usr/bin/env python3
"""
Monster Collector — Tkinter Edition (Battle Window)
---------------------------------------------------
- Overworld on main window
- Battles open in a separate Pokémon-style window layout
- Opponent stats top-left, opponent icon top-right
- Player stats bottom-left, player icon next to it
- Commands grouped bottom-right (Move1, Move2, Bag, Run)
- No external libraries beyond the Python standard library (tkinter)
"""
from core.game_controller import GameApp
import tkinter as tk

def main():
    try:
        app = GameApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except tk.TclError as e:
        print("Tkinter error:", e)
        print("If you're missing Tk, see installation tips: \n- Ubuntu/Debian: sudo apt install python3-tk\n- Fedora: sudo dnf install python3-tkinter\n- macOS (brew): brew install python-tk")

if __name__ == "__main__":
    main()
