"""Configuración de estilos TTK para la interfaz moderna."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def configurar_estilo(ventana_raiz: tk.Tk) -> None:
    """Aplica el tema 'clam' con colores y tipografías personalizados."""

    fondo_app = "#f4f6f8"
    fondo_tarjeta = "#ffffff"
    texto_principal = "#1f2937"
    texto_secundario = "#6b7280"
    acento = "#2563eb"
    acento_presionado = "#1d4ed8"
    acento_activo = "#3b82f6"

    estilo = ttk.Style(ventana_raiz)
    if "clam" in estilo.theme_names():
        estilo.theme_use("clam")

    ventana_raiz.configure(bg=fondo_app)

    estilo.configure("App.TFrame", background=fondo_app)
    estilo.configure("Card.TFrame", background=fondo_tarjeta, relief="flat")

    fuente_titulo = ("Sans", 16, "bold")
    fuente_normal = ("Sans", 10)
    fuente_negrita = ("Sans", 10, "bold")

    estilo.configure("Titulo.TLabel", background=fondo_tarjeta, foreground=texto_principal, font=fuente_titulo)
    estilo.configure("Subtitulo.TLabel", background=fondo_tarjeta, foreground=texto_secundario, font=fuente_normal)
    estilo.configure("Texto.TLabel", background=fondo_tarjeta, foreground=texto_principal, font=fuente_negrita)
    estilo.configure("TextoSuave.TLabel", background=fondo_tarjeta, foreground=texto_secundario, font=fuente_normal)
    estilo.configure("Estado.TLabel", background=fondo_tarjeta, foreground=texto_principal, font=fuente_negrita)
    estilo.configure("EstadoSecundario.TLabel", background=fondo_tarjeta, foreground=texto_secundario, font=fuente_normal)

    estilo.configure("TButton", padding=(12, 7), font=fuente_normal)
    estilo.configure(
        "Accent.TButton",
        background=acento,
        foreground="#ffffff",
        borderwidth=0,
        focusthickness=0,
        padding=(14, 8),
        font=fuente_negrita,
    )
    estilo.map(
        "Accent.TButton",
        background=[("pressed", acento_presionado), ("active", acento_activo)],
        foreground=[("disabled", "#d1d5db"), ("!disabled", "#ffffff")],
    )
