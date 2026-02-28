"""Notificaciones de escritorio."""

from __future__ import annotations

import shutil
import subprocess
from tkinter import messagebox


def notificar(titulo: str, mensaje: str) -> None:
    """Muestra una notificación del sistema o, como fallback, un messagebox."""
    if shutil.which("notify-send"):
        try:
            subprocess.run(
                ["notify-send", "-u", "normal", titulo, mensaje], check=False
            )
            return
        except Exception:
            pass
    try:
        messagebox.showinfo(titulo, mensaje)
    except Exception:
        pass
