from __future__ import annotations
import tkinter as tk
from typing import Optional, List, Callable

class TkTemplate(tk.Tk):

    def __init__(
        self, *,
        width: int = 800,
        height: int = 450,
        bg: str = "#0B0D12",
        title: str = "",
        topmost: bool = False,
        borderless: bool = False,
        center: bool = True,
        heartbeat: Optional[Callable[[], None]] = None,
        fps: int = 60,
    ):
        super().__init__()
        self._after_ids: List[str] = []

        self.title(title or "App")
        self.configure(bg=bg)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        if center:
            self.update_idletasks()
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            x, y = (sw - width) // 2, (sh - height) // 2
            self.geometry(f"{width}x{height}+{x}+{y}")
        if topmost:self.wm_attributes("-topmost", 1)
        if borderless:self.overrideredirect(True)

        self._heartbeat: Optional[Callable[[], None]] = heartbeat
        self._fps: int = max(1, int(fps))
        self._hb_id: Optional[str] = None
        self.protocol("WM_DELETE_WINDOW", self._safe_close)
        if self._heartbeat:self.start_heartbeat()

    def set_heartbeat(self, fn: Optional[Callable[[], None]]) -> None:
        self._heartbeat = fn

    def set_heartbeat_fps(self, fps: int) -> None:
        self._fps = max(1, int(fps))

    def start_heartbeat(self) -> None:
        if self._hb_id is not None or not self._heartbeat:return
        interval = max(1, int(1000 / self._fps))

        def _tick():
            if self._heartbeat is None:
                self._hb_id = None
                return
            try:
                self._heartbeat()
            finally:
                interval_ms = max(1, int(1000 / self._fps))
                self._hb_id = self.after(interval_ms, _tick)
        self._hb_id = self.after(interval, _tick)

    def stop_heartbeat(self) -> None:
        if self._hb_id is not None:
            try: self.after_cancel(self._hb_id)
            except Exception: pass
            self._hb_id = None

    def call_later(self, ms: int, fn):
        aid = self.after(ms, fn)
        self._after_ids.append(aid)
        return aid

    def _cancel_all(self):
        self.stop_heartbeat()
        for aid in self._after_ids:
            try: self.after_cancel(aid)
            except Exception: pass
        self._after_ids.clear()

    def _safe_close(self):
        self._cancel_all()
        try: self.destroy()
        except Exception: pass