"""Carga y guardado de configuración persistente."""

from __future__ import annotations

import json

from .constantes import RUTA_ARCHIVO_CONFIG, RUTA_DIRECTORIO_CONFIG


def cargar() -> dict:
    """Lee la configuración desde disco o devuelve un dict vacío."""
    if not RUTA_ARCHIVO_CONFIG.exists():
        return {}
    try:
        return json.loads(RUTA_ARCHIVO_CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return {}


def guardar(config: dict) -> None:
    """Persiste el diccionario de configuración a disco."""
    RUTA_DIRECTORIO_CONFIG.mkdir(parents=True, exist_ok=True)
    RUTA_ARCHIVO_CONFIG.write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8"
    )
