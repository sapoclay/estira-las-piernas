"""Atajos de teclado globales con Keybinder3."""

from __future__ import annotations

from .constantes import KEYBINDER_DISPONIBLE, _Keybinder


def inicializar() -> None:
    """Inicializa Keybinder (debe llamarse una vez al inicio)."""
    if not KEYBINDER_DISPONIBLE or _Keybinder is None:
        return
    _Keybinder.init()


def vincular(combinacion: str, callback) -> None:
    """Registra un atajo global. *callback* recibe (keystring)."""
    if not combinacion or not KEYBINDER_DISPONIBLE or _Keybinder is None:
        return
    try:
        exito = _Keybinder.bind(combinacion, callback)
        if exito:
            print(f"Atajo global registrado: {combinacion}")
        else:
            print(f"Aviso: no se pudo registrar el atajo {combinacion}")
    except Exception as e:
        print(f"Aviso: error al registrar atajo {combinacion}: {e}")


def desvincular(combinacion: str) -> None:
    """Elimina un atajo global previamente registrado."""
    if not combinacion or not KEYBINDER_DISPONIBLE or _Keybinder is None:
        return
    try:
        _Keybinder.unbind(combinacion)
    except Exception:
        pass
