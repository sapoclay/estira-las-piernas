#!/usr/bin/env python3
"""Estira las piernas – Recordatorio saludable para pausas activas.

Punto de entrada de la aplicación. La lógica está en el paquete ``src/``.
"""

import tkinter as tk

from src.aplicacion import AplicacionRecordatorioEstiramiento


def principal() -> None:
    ventana_raiz = tk.Tk()
    AplicacionRecordatorioEstiramiento(ventana_raiz)
    ventana_raiz.mainloop()


if __name__ == "__main__":
    principal()
