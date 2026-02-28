"""Constantes globales e importaciones opcionales de GObject Introspection."""

from __future__ import annotations

from pathlib import Path
from typing import Any

# ── Información de la aplicación ───────────────────────────────

NOMBRE_APP = "Estira las piernas"

# ── Intervalos (minutos) ───────────────────────────────────────

INTERVALO_PREDETERMINADO_MINUTOS = 45
INTERVALO_MINIMO_MINUTOS = 5
INTERVALO_MAXIMO_MINUTOS = 240

POMODORO_TRABAJO_PREDETERMINADO = 25
POMODORO_DESCANSO_PREDETERMINADO = 5

# ── Rutas ──────────────────────────────────────────────────────

RUTA_DIRECTORIO_CONFIG = Path.home() / ".config" / "estira-las-piernas"
RUTA_ARCHIVO_CONFIG = RUTA_DIRECTORIO_CONFIG / "config.json"
RUTA_ARCHIVO_ESTADISTICAS = RUTA_DIRECTORIO_CONFIG / "estadisticas.json"
RUTA_ICONO = Path(__file__).resolve().parent.parent / "img" / "logo.png"

# ── Sonidos del sistema ────────────────────────────────────────

SONIDOS_SISTEMA: dict[str, str] = {
    "Completado": "/usr/share/sounds/freedesktop/stereo/complete.oga",
    "Campana": "/usr/share/sounds/freedesktop/stereo/bell.oga",
    "Alarma": "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga",
    "Información": "/usr/share/sounds/freedesktop/stereo/dialog-information.oga",
    "Aviso": "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga",
    "Swing": "/usr/share/sounds/gnome/default/alerts/swing.ogg",
    "Click": "/usr/share/sounds/gnome/default/alerts/click.ogg",
    "Sin sonido": "",
}

# ── Atajos de teclado predeterminados ──────────────────────────

ATAJOS_PREDETERMINADOS: dict[str, str] = {
    "toggle_temporizador": "<Ctrl><Alt>p",
    "mostrar_ocultar": "<Ctrl><Alt>s",
}

# ── Importaciones opcionales de GI ─────────────────────────────
# Se inicializan a None para que el analizador estático no marque
# "posiblemente desvinculado" en el código que las usa.

AppIndicator3: Any = None
Gtk: Any = None
GLib: Any = None
_Keybinder: Any = None

APPINDICATOR_DISPONIBLE = False
KEYBINDER_DISPONIBLE = False

try:
    import gi

    gi.require_version("AppIndicator3", "0.1")
    gi.require_version("Gtk", "3.0")
    from gi.repository import AppIndicator3, Gtk, GLib  # type: ignore[no-redef]

    APPINDICATOR_DISPONIBLE = True
except Exception:
    pass

try:
    import gi  # noqa: F811

    gi.require_version("Keybinder", "3.0")
    from gi.repository import Keybinder as _Keybinder  # type: ignore[no-redef]

    KEYBINDER_DISPONIBLE = True
except Exception:
    pass
