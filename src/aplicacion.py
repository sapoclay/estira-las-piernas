"""Clase principal que orquesta la aplicación y construye la interfaz."""

from __future__ import annotations

import tkinter as tk
import webbrowser
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox, ttk

from .constantes import (
    ATAJOS_PREDETERMINADOS,
    INTERVALO_MAXIMO_MINUTOS,
    INTERVALO_MINIMO_MINUTOS,
    INTERVALO_PREDETERMINADO_MINUTOS,
    KEYBINDER_DISPONIBLE,
    NOMBRE_APP,
    POMODORO_DESCANSO_PREDETERMINADO,
    POMODORO_TRABAJO_PREDETERMINADO,
    RUTA_ICONO,
    SONIDOS_SISTEMA,
)
from . import atajos
from . import config as cfg
from . import notificaciones
from . import sonido
from .bandeja import BandejaSistema
from .estadisticas import Estadisticas
from .estilo import configurar_estilo


class AplicacionRecordatorioEstiramiento:
    """Ventana principal con pestañas, temporizador y bandeja del sistema."""

    def __init__(self, ventana_raiz: tk.Tk) -> None:
        self.ventana_raiz = ventana_raiz
        self.ventana_raiz.title(NOMBRE_APP)
        self.ventana_raiz.resizable(False, False)

        # Estado del temporizador
        self.trabajo_recordatorio: str | None = None
        self.trabajo_reloj: str | None = None
        self.proximo_recordatorio_en: datetime | None = None
        self.en_ejecucion = False

        # Pomodoro
        self.modo_pomodoro = False
        self.fase_pomodoro: str = "trabajo"
        self.pomodoros_completados = 0

        # Módulos auxiliares
        self.estadisticas = Estadisticas()
        self.bandeja = BandejaSistema()

        # Configuración persistente
        self.config = cfg.cargar()

        # Variables de tkinter
        self._crear_variables_tk()

        # Inicialización
        configurar_estilo(self.ventana_raiz)
        self._construir_interfaz()
        self.actualizar_estadisticas_ui()
        self._iniciar_bandeja()
        self._registrar_atajos_globales()

        self.ventana_raiz.protocol("WM_DELETE_WINDOW", self.al_pulsar_cerrar)

    # ── Variables de tkinter ───────────────────────────────────────

    def _crear_variables_tk(self) -> None:
        c = self.config
        self.variable_intervalo = tk.IntVar(
            value=c.get("interval_minutes", INTERVALO_PREDETERMINADO_MINUTOS)
        )
        self.variable_estado = tk.StringVar(value="Configurado y detenido")
        self.variable_cuenta_regresiva = tk.StringVar(value="Temporizador inactivo")

        self.variable_pomodoro_trabajo = tk.IntVar(
            value=c.get("pomodoro_trabajo", POMODORO_TRABAJO_PREDETERMINADO)
        )
        self.variable_pomodoro_descanso = tk.IntVar(
            value=c.get("pomodoro_descanso", POMODORO_DESCANSO_PREDETERMINADO)
        )
        self.variable_modo_pomodoro = tk.BooleanVar(
            value=c.get("modo_pomodoro", False)
        )

        self.variable_sonido = tk.StringVar(value=c.get("sonido", "Completado"))
        self.variable_sonido_personalizado = tk.StringVar(
            value=c.get("sonido_personalizado", "")
        )

        self.variable_pausas_hoy = tk.StringVar()
        self.variable_racha = tk.StringVar()
        self.variable_tiempo_activo = tk.StringVar()

        self.variable_atajo_toggle = tk.StringVar(
            value=c.get(
                "atajo_toggle", ATAJOS_PREDETERMINADOS["toggle_temporizador"]
            )
        )
        self.variable_atajo_ventana = tk.StringVar(
            value=c.get(
                "atajo_ventana", ATAJOS_PREDETERMINADOS["mostrar_ocultar"]
            )
        )

    # ── Configuración persistente ──────────────────────────────────

    def _guardar_config(self) -> None:
        self.config.update(
            {
                "interval_minutes": self.obtener_intervalo_actual(),
                "modo_pomodoro": self.variable_modo_pomodoro.get(),
                "pomodoro_trabajo": self.variable_pomodoro_trabajo.get(),
                "pomodoro_descanso": self.variable_pomodoro_descanso.get(),
                "sonido": self.variable_sonido.get(),
                "sonido_personalizado": self.variable_sonido_personalizado.get(),
                "atajo_toggle": self.variable_atajo_toggle.get(),
                "atajo_ventana": self.variable_atajo_ventana.get(),
            }
        )
        cfg.guardar(self.config)

    # ── Construcción de la interfaz ────────────────────────────────

    def _construir_interfaz(self) -> None:
        contenedor = ttk.Frame(self.ventana_raiz, style="App.TFrame", padding=12)
        contenedor.grid(row=0, column=0, sticky="nsew")
        self.ventana_raiz.columnconfigure(0, weight=1)
        self.ventana_raiz.rowconfigure(0, weight=1)

        tarjeta = ttk.Frame(contenedor, style="Card.TFrame", padding=14)
        tarjeta.grid(row=0, column=0, sticky="nsew")
        tarjeta.columnconfigure(0, weight=1)

        ttk.Label(tarjeta, text=NOMBRE_APP, style="Titulo.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            tarjeta,
            text="Recordatorio saludable para pausas activas",
            style="Subtitulo.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 10))

        pestanas = ttk.Notebook(tarjeta)
        pestanas.grid(row=2, column=0, sticky="nsew", pady=(0, 10))

        for texto, constructor in [
            (" Temporizador ", self._construir_tab_principal),
            (" Pomodoro ", self._construir_tab_pomodoro),
            (" Sonido ", self._construir_tab_sonido),
            (" Estadísticas ", self._construir_tab_estadisticas),
            (" Atajos ", self._construir_tab_atajos),
            (" Acerca de ", self._construir_tab_acerca_de),
        ]:
            tab = ttk.Frame(pestanas, style="Card.TFrame", padding=10)
            pestanas.add(tab, text=texto)
            tab.columnconfigure(0, weight=1)
            constructor(tab)

        ttk.Separator(tarjeta).grid(row=3, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(
            tarjeta, textvariable=self.variable_estado, style="Estado.TLabel"
        ).grid(row=4, column=0, sticky="w")
        ttk.Label(
            tarjeta,
            textvariable=self.variable_cuenta_regresiva,
            style="EstadoSecundario.TLabel",
        ).grid(row=5, column=0, sticky="w", pady=(4, 0))

    # ── Pestañas individuales ──────────────────────────────────────

    def _construir_tab_principal(self, padre: ttk.Frame) -> None:
        fila_intervalo = ttk.Frame(padre, style="Card.TFrame")
        fila_intervalo.grid(row=0, column=0, sticky="ew")

        ttk.Label(fila_intervalo, text="Intervalo", style="Texto.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Spinbox(
            fila_intervalo,
            from_=INTERVALO_MINIMO_MINUTOS,
            to=INTERVALO_MAXIMO_MINUTOS,
            textvariable=self.variable_intervalo,
            width=6,
            justify="center",
        ).grid(row=0, column=1, padx=(10, 8), sticky="w")
        ttk.Label(fila_intervalo, text="minutos", style="TextoSuave.TLabel").grid(
            row=0, column=2, sticky="w"
        )

        fila_botones = ttk.Frame(padre, style="Card.TFrame")
        fila_botones.grid(row=1, column=0, pady=(12, 0), sticky="ew")

        ttk.Button(
            fila_botones, text="▶  Iniciar", style="Accent.TButton", command=self.iniciar
        ).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(fila_botones, text="■  Detener", command=self.detener).grid(
            row=0, column=1, padx=(0, 10)
        )
        ttk.Button(
            fila_botones, text="🔔 Probar aviso", command=self._probar_aviso_ahora
        ).grid(row=0, column=2)

    def _construir_tab_pomodoro(self, padre: ttk.Frame) -> None:
        ttk.Checkbutton(
            padre,
            text="Activar modo Pomodoro",
            variable=self.variable_modo_pomodoro,
            command=self._al_cambiar_modo_pomodoro,
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            padre,
            text="Al activarlo se alternan ciclos de trabajo y descanso.",
            style="TextoSuave.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 10))

        for i, (etiqueta, var, maximo) in enumerate(
            [
                ("Trabajo", self.variable_pomodoro_trabajo, 120),
                ("Descanso", self.variable_pomodoro_descanso, 60),
            ],
            start=2,
        ):
            fila = ttk.Frame(padre, style="Card.TFrame")
            fila.grid(row=i, column=0, sticky="ew", pady=(0 if i == 2 else 8, 0))
            ttk.Label(fila, text=etiqueta, style="Texto.TLabel").grid(
                row=0, column=0, sticky="w"
            )
            ttk.Spinbox(
                fila, from_=1, to=maximo, textvariable=var, width=6, justify="center"
            ).grid(row=0, column=1, padx=(10, 8))
            ttk.Label(fila, text="min", style="TextoSuave.TLabel").grid(
                row=0, column=2, sticky="w"
            )

        self.etiqueta_fase_pomodoro = ttk.Label(
            padre, text="", style="TextoSuave.TLabel"
        )
        self.etiqueta_fase_pomodoro.grid(row=4, column=0, sticky="w", pady=(10, 0))

    def _construir_tab_sonido(self, padre: ttk.Frame) -> None:
        ttk.Label(padre, text="Sonido de aviso:", style="Texto.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        opciones = list(SONIDOS_SISTEMA.keys()) + ["Personalizado…"]
        combo = ttk.Combobox(
            padre,
            textvariable=self.variable_sonido,
            values=opciones,
            state="readonly",
            width=20,
        )
        combo.grid(row=1, column=0, sticky="w", pady=(6, 0))
        combo.bind("<<ComboboxSelected>>", self._al_cambiar_sonido)

        fila = ttk.Frame(padre, style="Card.TFrame")
        fila.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.entrada_sonido_personalizado = ttk.Entry(
            fila, textvariable=self.variable_sonido_personalizado, width=30
        )
        self.entrada_sonido_personalizado.grid(row=0, column=0, sticky="w")
        self.boton_explorar_sonido = ttk.Button(
            fila, text="Explorar…", command=self._explorar_sonido
        )
        self.boton_explorar_sonido.grid(row=0, column=1, padx=(8, 0))

        estado = (
            "normal" if self.variable_sonido.get() == "Personalizado…" else "disabled"
        )
        self.entrada_sonido_personalizado.configure(state=estado)
        self.boton_explorar_sonido.configure(state=estado)

        ttk.Button(
            padre, text="🔊 Probar sonido", command=self._probar_sonido
        ).grid(row=3, column=0, sticky="w", pady=(10, 0))

    def _construir_tab_estadisticas(self, padre: ttk.Frame) -> None:
        filas = [
            ("Pausas hoy:", self.variable_pausas_hoy),
            ("Racha de días:", self.variable_racha),
            ("Tiempo activo hoy:", self.variable_tiempo_activo),
        ]
        for i, (etiqueta, var) in enumerate(filas):
            ttk.Label(padre, text=etiqueta, style="Texto.TLabel").grid(
                row=i, column=0, sticky="w", pady=(6, 0)
            )
            ttk.Label(padre, textvariable=var, style="TextoSuave.TLabel").grid(
                row=i, column=1, sticky="w", padx=(10, 0), pady=(6, 0)
            )

    def _construir_tab_atajos(self, padre: ttk.Frame) -> None:
        if not KEYBINDER_DISPONIBLE:
            ttk.Label(
                padre,
                text="Keybinder3 no disponible.\n"
                "Instala gir1.2-keybinder-3.0 para atajos globales.",
                style="TextoSuave.TLabel",
            ).grid(row=0, column=0, sticky="w")
            return

        ttk.Label(
            padre,
            text="Atajos de teclado globales (formato GTK, ej: <Ctrl><Alt>p):",
            style="TextoSuave.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        ttk.Label(padre, text="Iniciar / Detener:", style="Texto.TLabel").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Entry(padre, textvariable=self.variable_atajo_toggle, width=20).grid(
            row=1, column=1, sticky="w", padx=(10, 0)
        )

        ttk.Label(padre, text="Mostrar / Ocultar:", style="Texto.TLabel").grid(
            row=2, column=0, sticky="w", pady=(8, 0)
        )
        ttk.Entry(padre, textvariable=self.variable_atajo_ventana, width=20).grid(
            row=2, column=1, sticky="w", padx=(10, 0), pady=(8, 0)
        )

        ttk.Button(padre, text="Aplicar atajos", command=self._aplicar_atajos).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(12, 0)
        )

    def _construir_tab_acerca_de(self, padre: ttk.Frame) -> None:
        padre.columnconfigure(0, weight=1)

        # Logo
        try:
            self._logo_imagen = tk.PhotoImage(file=str(RUTA_ICONO))
            lbl_logo = tk.Label(padre, image=self._logo_imagen, bg="#ffffff", bd=0)
            lbl_logo.grid(row=0, column=0, pady=(10, 8))
        except Exception:
            pass

        # Descripción
        descripcion = (
            f"{NOMBRE_APP}\n\n"
            "Aplicación de escritorio para Ubuntu que te recuerda\n"
            "levantarte y estirar las piernas periódicamente.\n\n"
            "Incluye temporizador configurable, modo Pomodoro,\n"
            "estadísticas, sonidos personalizables, atajos de\n"
            "teclado globales e icono en la bandeja del sistema."
        )
        ttk.Label(
            padre, text=descripcion, style="TextoSuave.TLabel",
            justify="center", wraplength=380,
        ).grid(row=1, column=0, pady=(0, 12))

        # Botón GitHub
        ttk.Button(
            padre,
            text="🌐 Abrir en GitHub",
            style="Accent.TButton",
            command=lambda: webbrowser.open("https://github.com/sapoclay/estira-las-piernas"),
        ).grid(row=2, column=0, pady=(0, 10))

    # ── Intervalo ──────────────────────────────────────────────────

    @staticmethod
    def normalizar_intervalo(valor: int) -> int:
        return max(INTERVALO_MINIMO_MINUTOS, min(INTERVALO_MAXIMO_MINUTOS, valor))

    def obtener_intervalo_actual(self) -> int:
        try:
            valor = int(self.variable_intervalo.get())
        except Exception:
            valor = INTERVALO_PREDETERMINADO_MINUTOS
        valor = self.normalizar_intervalo(valor)
        self.variable_intervalo.set(valor)
        return valor

    # ── Temporizador ───────────────────────────────────────────────

    def iniciar(self) -> None:
        self.modo_pomodoro = self.variable_modo_pomodoro.get()
        if self.modo_pomodoro:
            self.fase_pomodoro = "trabajo"
            self.pomodoros_completados = 0
            self._actualizar_etiqueta_pomodoro()

        self.en_ejecucion = True
        self._guardar_config()
        self._actualizar_texto_estado()
        self._programar_siguiente()

    def detener(self) -> None:
        self.en_ejecucion = False
        if self.trabajo_recordatorio is not None:
            self.ventana_raiz.after_cancel(self.trabajo_recordatorio)
            self.trabajo_recordatorio = None
        if self.trabajo_reloj is not None:
            self.ventana_raiz.after_cancel(self.trabajo_reloj)
            self.trabajo_reloj = None
        self.proximo_recordatorio_en = None
        self.variable_estado.set("Recordatorio detenido")
        self.variable_cuenta_regresiva.set("Temporizador inactivo")

    def alternar_temporizador(self) -> None:
        if self.en_ejecucion:
            self.detener()
        else:
            self.iniciar()

    def _obtener_intervalo_fase_actual(self) -> int:
        if self.modo_pomodoro:
            if self.fase_pomodoro == "trabajo":
                try:
                    return max(1, int(self.variable_pomodoro_trabajo.get()))
                except Exception:
                    return POMODORO_TRABAJO_PREDETERMINADO
            try:
                return max(1, int(self.variable_pomodoro_descanso.get()))
            except Exception:
                return POMODORO_DESCANSO_PREDETERMINADO
        return self.obtener_intervalo_actual()

    def _programar_siguiente(self) -> None:
        if self.trabajo_recordatorio is not None:
            self.ventana_raiz.after_cancel(self.trabajo_recordatorio)
        intervalo_min = self._obtener_intervalo_fase_actual()
        intervalo_ms = intervalo_min * 60 * 1000
        self.proximo_recordatorio_en = datetime.now() + timedelta(
            milliseconds=intervalo_ms
        )
        self.trabajo_recordatorio = self.ventana_raiz.after(
            intervalo_ms, self._al_recordatorio
        )
        self._actualizar_cuenta_regresiva()

    def _actualizar_cuenta_regresiva(self) -> None:
        if not self.en_ejecucion or self.proximo_recordatorio_en is None:
            self.variable_cuenta_regresiva.set("Temporizador inactivo")
            self.trabajo_reloj = None
            return
        restante = self.proximo_recordatorio_en - datetime.now()
        total_segundos = max(0, int(restante.total_seconds()))
        minutos, segundos = divmod(total_segundos, 60)
        prefijo = ""
        if self.modo_pomodoro:
            prefijo = "🍅 " if self.fase_pomodoro == "trabajo" else "☕ "
        self.variable_cuenta_regresiva.set(
            f"{prefijo}Próximo aviso en {minutos:02d}:{segundos:02d}"
        )
        self.trabajo_reloj = self.ventana_raiz.after(
            1000, self._actualizar_cuenta_regresiva
        )

    def _al_recordatorio(self) -> None:
        if not self.en_ejecucion:
            return
        self.estadisticas.registrar_pausa()
        self.actualizar_estadisticas_ui()
        if self.modo_pomodoro:
            if self.fase_pomodoro == "trabajo":
                self.pomodoros_completados += 1
                notificaciones.notificar(
                    "Descanso", "¡Buen trabajo! Tómate un descanso."
                )
                self.fase_pomodoro = "descanso"
            else:
                notificaciones.notificar(
                    "A trabajar", "El descanso terminó. ¡Vamos de nuevo!"
                )
                self.fase_pomodoro = "trabajo"
            self._actualizar_etiqueta_pomodoro()
            self._actualizar_texto_estado()
        else:
            notificaciones.notificar(
                "Hora de moverse",
                "Levántate y estira las piernas unos minutos.",
            )
        self._reproducir_pitido()
        self._programar_siguiente()

    def _probar_aviso_ahora(self) -> None:
        notificaciones.notificar(
            "Hora de moverse",
            "Levántate y estira las piernas unos minutos.",
        )
        self._reproducir_pitido()

    def _actualizar_texto_estado(self) -> None:
        if self.modo_pomodoro:
            fase = "Trabajo" if self.fase_pomodoro == "trabajo" else "Descanso"
            self.variable_estado.set(
                f"Pomodoro: {fase} · Completados: {self.pomodoros_completados}"
            )
        else:
            intervalo = self.obtener_intervalo_actual()
            self.variable_estado.set(f"Recordatorio activo cada {intervalo} min")

    # ── Pomodoro ───────────────────────────────────────────────────

    def _al_cambiar_modo_pomodoro(self) -> None:
        if self.en_ejecucion:
            self.detener()
        self._guardar_config()

    def _actualizar_etiqueta_pomodoro(self) -> None:
        if hasattr(self, "etiqueta_fase_pomodoro"):
            fase = "🍅 Trabajo" if self.fase_pomodoro == "trabajo" else "☕ Descanso"
            self.etiqueta_fase_pomodoro.configure(
                text=f"Fase actual: {fase} · Pomodoros: {self.pomodoros_completados}"
            )

    # ── Sonido ─────────────────────────────────────────────────────

    def _al_cambiar_sonido(self, _evento=None) -> None:
        es_personalizado = self.variable_sonido.get() == "Personalizado…"
        estado = "normal" if es_personalizado else "disabled"
        self.entrada_sonido_personalizado.configure(state=estado)
        self.boton_explorar_sonido.configure(state=estado)
        self._guardar_config()

    def _explorar_sonido(self) -> None:
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de sonido",
            filetypes=[("Audio", "*.oga *.ogg *.wav *.mp3"), ("Todos", "*.*")],
        )
        if ruta:
            self.variable_sonido_personalizado.set(ruta)
            self._guardar_config()

    def _probar_sonido(self) -> None:
        self._reproducir_pitido()

    def _reproducir_pitido(self) -> None:
        ruta = sonido.obtener_ruta(
            self.variable_sonido.get(), self.variable_sonido_personalizado.get()
        )
        sonido.reproducir(ruta)

    # ── Estadísticas ───────────────────────────────────────────────

    def actualizar_estadisticas_ui(self) -> None:
        pausas = self.estadisticas.pausas_hoy()
        racha = self.estadisticas.racha_dias()
        tiempo = self.estadisticas.tiempo_desde_primera_pausa_hoy()
        self.variable_pausas_hoy.set(str(pausas))
        self.variable_racha.set(
            f"{racha} día{'s' if racha != 1 else ''} "
            f"consecutivo{'s' if racha != 1 else ''}"
        )
        self.variable_tiempo_activo.set(tiempo)

    # ── Atajos de teclado globales ─────────────────────────────────

    def _registrar_atajos_globales(self) -> None:
        atajos.inicializar()
        atajos.vincular(
            self.variable_atajo_toggle.get(), self._callback_atajo_toggle
        )
        atajos.vincular(
            self.variable_atajo_ventana.get(), self._callback_atajo_ventana
        )

    def _callback_atajo_toggle(self, _keystring) -> None:
        self.ventana_raiz.after(0, self.alternar_temporizador)

    def _callback_atajo_ventana(self, _keystring) -> None:
        self.ventana_raiz.after(0, self.alternar_ventana)

    def _aplicar_atajos(self) -> None:
        atajos.desvincular(self.config.get("atajo_toggle", ""))
        atajos.desvincular(self.config.get("atajo_ventana", ""))
        atajos.vincular(
            self.variable_atajo_toggle.get().strip(), self._callback_atajo_toggle
        )
        atajos.vincular(
            self.variable_atajo_ventana.get().strip(), self._callback_atajo_ventana
        )
        self._guardar_config()
        messagebox.showinfo("Atajos", "Atajos globales actualizados.")

    # ── Bandeja del sistema ────────────────────────────────────────

    def _iniciar_bandeja(self) -> None:
        self.bandeja.iniciar(
            al_alternar_ventana=lambda: self.ventana_raiz.after(
                0, self.alternar_ventana
            ),
            al_alternar_temporizador=lambda: self.ventana_raiz.after(
                0, self.alternar_temporizador
            ),
            al_salir=lambda: self.ventana_raiz.after(0, self.salir_aplicacion),
        )

    def alternar_ventana(self) -> None:
        if self.ventana_raiz.state() == "withdrawn":
            self._mostrar_ventana()
        else:
            self._ocultar_ventana()

    def _mostrar_ventana(self) -> None:
        self.ventana_raiz.deiconify()
        self.ventana_raiz.lift()
        try:
            self.ventana_raiz.focus_force()
        except Exception:
            pass

    def _ocultar_ventana(self) -> None:
        self.ventana_raiz.withdraw()

    # ── Cierre ─────────────────────────────────────────────────────

    def al_pulsar_cerrar(self) -> None:
        if self.bandeja.activa:
            self._ocultar_ventana()
        else:
            self.salir_aplicacion()

    def salir_aplicacion(self) -> None:
        self._guardar_config()
        self.detener()
        self.bandeja.detener()
        self.ventana_raiz.destroy()
