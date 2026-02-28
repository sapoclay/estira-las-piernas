"""Icono de bandeja del sistema con AppIndicator3."""

from __future__ import annotations

import threading
from typing import Any, Callable

from .constantes import (
    APPINDICATOR_DISPONIBLE,
    AppIndicator3,
    GLib,
    Gtk,
    NOMBRE_APP,
    RUTA_ICONO,
)


class BandejaSistema:
    """Gestiona el icono en la bandeja y su menú contextual."""

    def __init__(self) -> None:
        self.indicador = None
        self._hilo_gtk: threading.Thread | None = None
        self._bucle = None  # GLib.MainLoop

    @property
    def activa(self) -> bool:
        """Devuelve True si el indicador está creado y visible."""
        return self.indicador is not None

    def iniciar(
        self,
        al_alternar_ventana: Callable[[], Any],
        al_alternar_temporizador: Callable[[], Any],
        al_salir: Callable[[], Any],
    ) -> None:
        """Crea el indicador, menú y arranca el bucle GTK en segundo plano."""
        if (
            not APPINDICATOR_DISPONIBLE
            or AppIndicator3 is None
            or Gtk is None
            or GLib is None
        ):
            print("Aviso: AppIndicator3 no disponible; sin icono de bandeja.")
            return

        if not RUTA_ICONO.exists():
            print(f"Aviso: no se encontró el icono en {RUTA_ICONO}")
            return

        self.indicador = AppIndicator3.Indicator.new(
            "estira-las-piernas",
            str(RUTA_ICONO),
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self.indicador.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicador.set_title(NOMBRE_APP)

        menu_gtk = Gtk.Menu()

        item_mostrar = Gtk.MenuItem(label="Mostrar / Ocultar ventana")
        item_mostrar.connect("activate", lambda _w: al_alternar_ventana())
        menu_gtk.append(item_mostrar)

        item_toggle = Gtk.MenuItem(label="Iniciar / Detener")
        item_toggle.connect("activate", lambda _w: al_alternar_temporizador())
        menu_gtk.append(item_toggle)

        menu_gtk.append(Gtk.SeparatorMenuItem())

        item_salir = Gtk.MenuItem(label="Salir")
        item_salir.connect("activate", lambda _w: al_salir())
        menu_gtk.append(item_salir)

        menu_gtk.show_all()
        self.indicador.set_menu(menu_gtk)

        self._bucle = GLib.MainLoop()
        self._hilo_gtk = threading.Thread(target=self._ejecutar_bucle, daemon=True)
        self._hilo_gtk.start()

    def _ejecutar_bucle(self) -> None:
        if self._bucle is not None:
            self._bucle.run()

    def detener(self) -> None:
        """Para el bucle GTK y libera el indicador."""
        if self._bucle is not None:
            try:
                self._bucle.quit()
            except Exception:
                pass
            self._bucle = None
        self.indicador = None
