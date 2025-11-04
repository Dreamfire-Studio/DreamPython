from __future__ import annotations
import tkinter as tk
from typing import Iterable, Callable, Optional, List, Dict
from PIL import Image, ImageTk

def create_canvas(root: tk.Tk, *, width: int, height: int, bg: str) -> tk.Canvas:
    c = tk.Canvas(root, width=width, height=height, bg=bg, highlightthickness=0, bd=0)
    c.pack(fill="both", expand=True)
    c._imrefs: List[ImageTk.PhotoImage] = []
    c._bg_rgba = _hex_to_rgba(bg)
    c._center = (width // 2, height // 2)
    c._wh = (width, height)
    return c

def create_button(parent: tk.Widget, text: str, command: Callable[[], None]) -> tk.Button:
    b = tk.Button(parent, text=text, command=command)
    b.pack()
    return b

def create_dropdown(parent: tk.Widget, values: Iterable[str], var: Optional[tk.StringVar]=None) -> tk.OptionMenu:
    var = var or tk.StringVar(value=next(iter(values), ""))
    w = tk.OptionMenu(parent, var, *values)
    w.pack()
    return w

def _hex_to_rgba(h: str) -> tuple[int, int, int, int]:
    h = h.lstrip("#")
    if len(h) == 6:
        r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        return (r,g,b,255)
    if len(h) == 8:
        r,g,b,a = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), int(h[6:8],16)
        return (r,g,b,a)
    return (0,0,0,255)

def _ease_out_cubic(t: float) -> float:
    return 1.0 - (1.0 - t) ** 3

def _fit_size(iw: int, ih: int, cw: int, ch: int, fit: str) -> tuple[int, int]:
    if fit == "none": return iw, ih
    aspect = iw / max(1, ih)
    if fit == "cover":
        if cw / ch > aspect: h = ch; w = int(h * aspect)
        else: w = cw; h = int(w / aspect)
        s = max(cw / w, ch / h)
        return int(w * s), int(h * s)
    if cw / ch > aspect: h = ch; w = int(h * aspect)
    else: w = cw; h = int(w / aspect)
    return w, h

def animate_logo(
    canvas: tk.Canvas,
    path: str,
    *,
    mode: str = "zoom_out_fade",
    duration_ms: int = 800,
    hold_ms: int = 300,
    start_scale: float = 1.8,
    end_scale: float = 1.0,
    fade: bool = True,
    fit: str = "contain",
    max_scale: float = 2.5,
    fps: int = 60,
    on_done: Callable[[], None] | None = None,
) -> None:
    """Animate ONE image on the canvas. Composites onto a bg-colored buffer each frame."""
    cw, ch = canvas._wh
    cx, cy = canvas._center
    bg_rgba = canvas._bg_rgba

    base = Image.open(path).convert("RGBA")
    bw, bh = _fit_size(base.width, base.height, cw, ch, fit)

    total_frames = max(1, round((duration_ms / 1000.0) * max(1, fps)))
    interval = max(1, int(1000 / max(1, fps)))

    item = canvas.create_image(cx, cy, image=None)

    def frame_params(t: float) -> tuple[float, int, int]:
        # (scale, alpha, y_offset)
        if mode == "zoom_in":
            return (end_scale + (start_scale - end_scale) * (1 - t), 255, 0)
        if mode == "fade_in":
            return (end_scale, int(255 * t), 0)
        if mode == "slide_up":
            return (end_scale, int(255 * t) if fade else 255, int(40 * (1 - t)))
        # default zoom_out_fade
        return (start_scale + (end_scale - start_scale) * t, int(255 * t) if fade else 255, 0)

    def show(i: int):
        t = _ease_out_cubic(i / max(1, total_frames - 1))
        scale, alpha, dy = frame_params(t)
        scale = max(0.01, min(max_scale, scale))

        rw, rh = max(1, int(bw * scale)), max(1, int(bh * scale))

        off = Image.new("RGBA", (cw, ch), bg_rgba)
        fr = base.resize((rw, rh), Image.LANCZOS)

        if alpha < 255:
            r, g, b, a = fr.split()
            a = a.point(lambda px: int(px * (alpha / 255.0)))
            fr = Image.merge("RGBA", (r, g, b, a))

        x = cx - rw // 2
        y = cy - rh // 2 + dy
        off.alpha_composite(fr, (x, y))

        tkimg = ImageTk.PhotoImage(off)
        canvas._imrefs.append(tkimg)        # keep ref alive
        canvas.itemconfigure(item, image=tkimg)

        if i < total_frames - 1:
            canvas.after(interval, lambda: show(i + 1))
        else:
            # small hold so next image feels deliberate
            canvas.after(max(0, hold_ms), lambda: (on_done and on_done()))

    show(0)

def animate_sequence(
    canvas: tk.Canvas,
    sequence: List[Dict],
    *,
    fps: int = 60,
    on_complete: Callable[[], None] | None = None,
) -> None:
    idx = 0

    def _next():
        nonlocal idx
        if idx >= len(sequence):
            if on_complete:
                on_complete()
            return
        cfg = sequence[idx]; idx += 1
        animate_logo(
            canvas,
            cfg["path"],
            mode=cfg.get("mode", "zoom_out_fade"),
            duration_ms=int(cfg.get("duration_ms", 800)),
            hold_ms=int(cfg.get("hold_ms", 300)),
            start_scale=float(cfg.get("start_scale", 1.8)),
            end_scale=float(cfg.get("end_scale", 1.0)),
            fade=bool(cfg.get("fade", True)),
            fit=cfg.get("fit", "contain"),
            max_scale=float(cfg.get("max_scale", 2.5)),
            fps=fps,
            on_done=_next,
        )

    _next()