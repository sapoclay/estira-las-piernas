"""Reproducción de sonidos de aviso."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .constantes import SONIDOS_SISTEMA


def obtener_ruta(nombre_sonido: str, ruta_personalizada: str = "") -> str:
    """Resuelve la ruta del archivo de sonido según la selección del usuario."""
    if nombre_sonido == "Personalizado…":
        return ruta_personalizada
    return SONIDOS_SISTEMA.get(nombre_sonido, "")


def reproducir(ruta: str) -> None:
    """Reproduce un archivo de sonido; usa campana de terminal como fallback."""
    if not ruta:
        return

    if not Path(ruta).exists():
        print(f"Aviso: archivo de sonido no encontrado: {ruta}")
        print("\a", end="", flush=True)
        return

    for reproductor, args_extra, condicion in [
        ("paplay", [], True),
        ("aplay", [], ruta.endswith(".wav")),
        ("canberra-gtk-play", ["-f"], True),
    ]:
        if condicion and shutil.which(reproductor):
            try:
                subprocess.Popen([reproductor, *args_extra, ruta])
                return
            except Exception:
                continue

    # Fallback: campana de terminal
    print("\a", end="", flush=True)
