# Estira las piernas (Ubuntu)

<img width="560" height="590" alt="estira-las-piernas" src="https://github.com/user-attachments/assets/e38301a8-108b-4984-a02b-864679cbfd85" />

Aplicación de escritorio para Ubuntu que recuerda al usuario levantarse periódicamente mediante:

- Notificación de escritorio
- Pitido/sonido configurable
- Modo Pomodoro (ciclos trabajo/descanso)
- Estadísticas diarias y rachas
- Atajos de teclado globales
- Icono en la bandeja del sistema

El intervalo es configurable por el usuario y por defecto está en **45 minutos**.

## Requisitos

- Ubuntu con entorno gráfico
- Python 3 (incluye `tkinter` en la mayoría de instalaciones)
- Dependencias para bandeja del sistema:
  - `gir1.2-appindicator3-0.1` (normalmente ya incluido en Ubuntu)
- Opcional para atajos de teclado globales:
  - `gir1.2-keybinder-3.0`
- Opcional para sonido y notificaciones:
  - `notify-send` (`libnotify-bin`)
  - `paplay` (`pulseaudio-utils`) o `canberra-gtk-play` (`libcanberra-gtk3-module`)

Instalación de dependencias opcionales:

```bash
sudo apt install gir1.2-appindicator3-0.1 gir1.2-keybinder-3.0
```

## Ejecutar

```bash
python3 estira_las_piernas.py
```

## Instalar como app de escritorio

```bash
chmod +x install_desktop_entry.sh
./install_desktop_entry.sh
```

Después, abre el menú de aplicaciones y busca **Estira las piernas**.

Este comando también activa el autoarranque al iniciar sesión en Ubuntu.

### Opciones de autoarranque

- Instalar solo lanzador (sin autoarranque):

```bash
./install_desktop_entry.sh --sin-autoarranque
```

- Desactivar autoarranque:

```bash
./install_desktop_entry.sh --desactivar-autoarranque
```

También se mantienen por compatibilidad las opciones anteriores:

- `--no-autostart`
- `--disable-autostart`

### Desinstalar

Para eliminar el lanzador, el autoarranque y la configuración guardada:

```bash
./install_desktop_entry.sh --desinstalar
```

También disponible como `--uninstall`.

Si además quieres eliminar los archivos del programa, borra la carpeta del proyecto manualmente.

## Funcionalidades

### Temporizador básico

Configura el intervalo de recordatorio (5–240 minutos) y pulsa **Iniciar**. Al vencer el temporizador se muestra una notificación de escritorio y se reproduce un sonido.

### Modo Pomodoro

Actívalo desde la pestaña **Pomodoro**. Alterna automáticamente entre ciclos de trabajo (25 min por defecto) y descanso (5 min por defecto), ambos configurables. Se muestra la fase actual y el número de pomodoros completados.

### Sonido personalizable

Desde la pestaña **Sonido** puedes elegir entre varios sonidos del sistema o seleccionar un archivo de audio propio. También puedes silenciar los avisos seleccionando "Sin sonido".

### Estadísticas

La pestaña **Estadísticas** muestra:

- Pausas realizadas hoy
- Racha de días consecutivos con pausas
- Tiempo activo desde la primera pausa del día

Los datos se guardan en `~/.config/estira-las-piernas/estadisticas.json`.

### Atajos de teclado globales

Desde la pestaña **Atajos** puedes configurar combinaciones de teclas globales (funcionan sin tener la ventana en primer plano):

- **Iniciar / Detener** temporizador (por defecto: `Ctrl+Alt+P`)
- **Mostrar / Ocultar** ventana (por defecto: `Ctrl+Alt+S`)

Requiere `gir1.2-keybinder-3.0`.

### Bandeja del sistema

La app muestra un icono en la bandeja del sistema. Pulsar la **X** de la ventana la oculta a la bandeja en vez de cerrarla. Desde el menú del icono puedes mostrar/ocultar la ventana, iniciar/detener el temporizador o salir.

### Acerca de

La pestaña **Acerca de** muestra el logo de la aplicación, una breve descripción y un botón para abrir el repositorio en GitHub.

## Estructura del proyecto

```
estira_las_piernas.py          ← Punto de entrada
src/
├── __init__.py
├── constantes.py              ← Constantes e imports de GI
├── config.py                  ← Carga/guardado de configuración
├── estadisticas.py            ← Estadísticas diarias y rachas
├── sonido.py                  ← Reproducción de sonidos
├── notificaciones.py          ← Notificaciones de escritorio
├── atajos.py                  ← Atajos globales (Keybinder3)
├── bandeja.py                 ← Icono en bandeja (AppIndicator3)
├── estilo.py                  ← Estilos TTK
└── aplicacion.py              ← Clase principal (UI + lógica)
img/
└── logo.png                   ← Icono de la aplicación
```

## Configuración

La app guarda toda la configuración en:

`~/.config/estira-las-piernas/config.json`

## Notas

- Intervalo mínimo: 5 minutos
- Intervalo máximo: 240 minutos
- Botón **Probar aviso** para verificar notificación y pitido sin esperar al temporizador
- Al pulsar `Ctrl+C` en la terminal la aplicación se cierra limpiamente guardando la configuración
- El script de instalación es compatible con `sh` y `bash`
