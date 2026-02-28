#!/usr/bin/env python3
"""Estira las piernas – Recordatorio saludable para pausas activas.

Punto de entrada de la aplicación. La lógica está en el paquete ``src/``.
"""

import signal
import sys
import tkinter as tk

from src.aplicacion import AplicacionRecordatorioEstiramiento


def principal() -> None:
    ventana_raiz = tk.Tk()
    app = AplicacionRecordatorioEstiramiento(ventana_raiz)

    def _al_interrumpir(*_args) -> None:
        print("\n👋 Cerrando Estira las piernas…")
        try:
            app.salir_aplicacion()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, _al_interrumpir)
    signal.signal(signal.SIGTERM, _al_interrumpir)

    try:
        ventana_raiz.mainloop()
    except KeyboardInterrupt:
        _al_interrumpir()


if __name__ == "__main__":
    principal()
