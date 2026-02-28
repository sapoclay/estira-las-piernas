"""Gestión de estadísticas diarias y rachas de pausas."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from .constantes import RUTA_ARCHIVO_ESTADISTICAS, RUTA_DIRECTORIO_CONFIG


class Estadisticas:
    """Registra pausas diarias, calcula rachas y tiempo activo."""

    def __init__(self) -> None:
        self.datos: dict = self._cargar()

    # ── Persistencia ───────────────────────────────────────────

    @staticmethod
    def _cargar() -> dict:
        if not RUTA_ARCHIVO_ESTADISTICAS.exists():
            return {"dias": {}}
        try:
            return json.loads(
                RUTA_ARCHIVO_ESTADISTICAS.read_text(encoding="utf-8")
            )
        except Exception:
            return {"dias": {}}

    def guardar(self) -> None:
        RUTA_DIRECTORIO_CONFIG.mkdir(parents=True, exist_ok=True)
        RUTA_ARCHIVO_ESTADISTICAS.write_text(
            json.dumps(self.datos, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ── Registro ───────────────────────────────────────────────

    def registrar_pausa(self) -> None:
        hoy = date.today().isoformat()
        if hoy not in self.datos.setdefault("dias", {}):
            self.datos["dias"][hoy] = {
                "pausas": 0,
                "primera": None,
                "ultima": None,
            }
        entrada = self.datos["dias"][hoy]
        entrada["pausas"] += 1
        ahora = datetime.now().strftime("%H:%M:%S")
        if entrada["primera"] is None:
            entrada["primera"] = ahora
        entrada["ultima"] = ahora
        self.guardar()

    # ── Consultas ──────────────────────────────────────────────

    def pausas_hoy(self) -> int:
        hoy = date.today().isoformat()
        return self.datos.get("dias", {}).get(hoy, {}).get("pausas", 0)

    def racha_dias(self) -> int:
        dias_ordenados = sorted(self.datos.get("dias", {}).keys(), reverse=True)
        if not dias_ordenados:
            return 0
        racha = 0
        dia_actual = date.today()
        for iso in dias_ordenados:
            try:
                d = date.fromisoformat(iso)
            except ValueError:
                continue
            if d == dia_actual:
                racha += 1
                dia_actual -= timedelta(days=1)
            elif d < dia_actual:
                break
        return racha

    def tiempo_desde_primera_pausa_hoy(self) -> str:
        hoy = date.today().isoformat()
        primera = self.datos.get("dias", {}).get(hoy, {}).get("primera")
        if primera is None:
            return "—"
        try:
            inicio = datetime.strptime(primera, "%H:%M:%S").replace(
                year=date.today().year,
                month=date.today().month,
                day=date.today().day,
            )
            delta = datetime.now() - inicio
            horas, resto = divmod(int(delta.total_seconds()), 3600)
            minutos, _ = divmod(resto, 60)
            return f"{horas}h {minutos}m"
        except Exception:
            return "—"
