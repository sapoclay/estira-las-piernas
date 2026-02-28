"""Ventana de descanso a pantalla completa para el modo Pomodoro."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime, timedelta
from typing import Callable


class VentanaDescanso:
    """Muestra una ventana fullscreen con cuenta atrás durante el descanso."""

    def __init__(
        self,
        ventana_padre: tk.Tk,
        minutos_descanso: int,
        al_finalizar: Callable[[], None],
    ) -> None:
        self._al_finalizar = al_finalizar
        self._trabajo_reloj: str | None = None

        self.ventana = tk.Toplevel(ventana_padre)
        self.ventana.title("☕ Descanso")
        self.ventana.configure(bg="#1e293b")
        self.ventana.attributes("-fullscreen", True)
        self.ventana.attributes("-topmost", True)

        # Evitar que se cierre con Alt+F4 (debe esperar al fin del descanso)
        self.ventana.protocol("WM_DELETE_WINDOW", lambda: None)

        # Permitir cerrar con Escape si el usuario realmente quiere saltarse el descanso
        self.ventana.bind("<Escape>", lambda _e: self._cerrar_anticipado())

        # ── Contenido centrado ─────────────────────────────────────

        marco = tk.Frame(self.ventana, bg="#1e293b")
        marco.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            marco,
            text="☕",
            font=("Sans", 72),
            bg="#1e293b",
            fg="#ffffff",
        ).pack(pady=(0, 10))

        tk.Label(
            marco,
            text="¡Hora de descansar!",
            font=("Sans", 36, "bold"),
            bg="#1e293b",
            fg="#ffffff",
        ).pack(pady=(0, 8))

        tk.Label(
            marco,
            text="Levántate, estira las piernas y descansa la vista.",
            font=("Sans", 16),
            bg="#1e293b",
            fg="#94a3b8",
        ).pack(pady=(0, 30))

        self._var_cuenta = tk.StringVar()
        tk.Label(
            marco,
            textvariable=self._var_cuenta,
            font=("Sans", 48, "bold"),
            bg="#1e293b",
            fg="#38bdf8",
        ).pack(pady=(0, 30))

        tk.Label(
            marco,
            text="Pulsa Escape para saltar el descanso",
            font=("Sans", 11),
            bg="#1e293b",
            fg="#475569",
        ).pack()

        # ── Cuenta atrás ──────────────────────────────────────────

        self._fin = datetime.now() + timedelta(minutes=minutos_descanso)
        self._actualizar_cuenta()

    def _actualizar_cuenta(self) -> None:
        restante = self._fin - datetime.now()
        total_seg = max(0, int(restante.total_seconds()))
        minutos, segundos = divmod(total_seg, 60)
        self._var_cuenta.set(f"{minutos:02d}:{segundos:02d}")

        if total_seg <= 0:
            self._cerrar()
            return

        self._trabajo_reloj = self.ventana.after(1000, self._actualizar_cuenta)

    def _cerrar(self) -> None:
        if self._trabajo_reloj is not None:
            self.ventana.after_cancel(self._trabajo_reloj)
            self._trabajo_reloj = None
        self.ventana.destroy()
        self._al_finalizar()

    def cerrar(self) -> None:
        """Cierra la ventana desde fuera (p.ej. al detener el temporizador)."""
        if self._trabajo_reloj is not None:
            self.ventana.after_cancel(self._trabajo_reloj)
            self._trabajo_reloj = None
        self.ventana.destroy()

    def _cerrar_anticipado(self) -> None:
        """El usuario pulsa Escape para saltarse el descanso."""
        self._cerrar()
