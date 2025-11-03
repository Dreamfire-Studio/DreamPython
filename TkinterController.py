from __future__ import annotations
from typing import Tuple, Dict, Any
import sys

USING_CTK = False
try:
    import customtkinter as ctk
    USING_CTK = True
except Exception:
    USING_CTK = False

import tkinter as tk

def _center_window(win: tk.Tk, width: int, height: int) -> None:
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    x, y = (sw // 2) - (width // 2), (sh // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def build_window(cfg: Dict[str, Any]) -> Tuple[tk.Tk, tk.Canvas]:
    wcfg = cfg["window"]
    width, height = int(wcfg["width"]), int(wcfg["height"])
    bg = wcfg.get("bg", "#000000")

    if USING_CTK:
        ctk.set_appearance_mode("dark")
        root = ctk.CTk()
        root.configure(fg_color=bg)
    else:
        root = tk.Tk()
        root.configure(bg=bg)

    root.overrideredirect(bool(wcfg.get("borderless", True)))
    if wcfg.get("topmost", True):
        root.wm_attributes("-topmost", 1)

    root.geometry(f"{width}x{height}")
    if wcfg.get("center", True):
        _center_window(root, width, height)

    try:
        if sys.platform.startswith("win"):
            root.tk.call('tk', 'scaling', 1.0)
    except Exception:
        pass

    canvas = tk.Canvas(root, width=width, height=height, bg=bg, highlightthickness=0, bd=0)
    canvas.pack(fill="both", expand=True)
    return root, canvas