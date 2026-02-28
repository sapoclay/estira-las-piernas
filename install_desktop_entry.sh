#!/usr/bin/env bash
set -eu

RUTA_APP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVO_APP="$RUTA_APP/estira_las_piernas.py"
RUTA_LANZADORES="$HOME/.local/share/applications"
ARCHIVO_LANZADOR="$RUTA_LANZADORES/estira-las-piernas.desktop"
RUTA_AUTOARRANQUE="$HOME/.config/autostart"
ARCHIVO_AUTOARRANQUE="$RUTA_AUTOARRANQUE/estira-las-piernas.desktop"
RUTA_ICONO="$RUTA_APP/img/logo.png"

INSTALAR_AUTOARRANQUE=true
DESACTIVAR_AUTOARRANQUE=false
DESINSTALAR=false

for arg in "$@"; do
	case "$arg" in
		--sin-autoarranque|--no-autostart)
			INSTALAR_AUTOARRANQUE=false
			;;
		--desactivar-autoarranque|--disable-autostart)
			DESACTIVAR_AUTOARRANQUE=true
			;;
		--desinstalar|--uninstall)
			DESINSTALAR=true
			;;
		*)
			echo "Opción no reconocida: $arg"
			echo "Uso: $0 [--sin-autoarranque|--no-autostart] [--desactivar-autoarranque|--disable-autostart] [--desinstalar|--uninstall]"
			exit 1
			;;
	esac
done

# ── Desinstalación ─────────────────────────────────────────────
if [ "$DESINSTALAR" = true ]; then
	echo "Desinstalando Estira las piernas…"
	rm -f "$ARCHIVO_LANZADOR"
	rm -f "$ARCHIVO_AUTOARRANQUE"
	rm -rf "$HOME/.config/estira-las-piernas"
	update-desktop-database "$RUTA_LANZADORES" >/dev/null 2>&1 || true
	echo "✔ Lanzador eliminado: $ARCHIVO_LANZADOR"
	echo "✔ Autoarranque eliminado: $ARCHIVO_AUTOARRANQUE"
	echo "✔ Configuración eliminada: $HOME/.config/estira-las-piernas"
	echo ""
	echo "Si deseas eliminar también los archivos del programa:"
	echo "  rm -rf $RUTA_APP"
	exit 0
fi

mkdir -p "$RUTA_LANZADORES"

cat > "$ARCHIVO_LANZADOR" <<EOF
[Desktop Entry]
Name=Estira las piernas
Comment=Recordatorio para levantarte y estirarte
Exec=python3 "$ARCHIVO_APP"
Icon=$RUTA_ICONO
Terminal=false
Type=Application
Categories=Utility;Health;
StartupNotify=true
EOF

chmod +x "$ARCHIVO_APP"
update-desktop-database "$RUTA_LANZADORES" >/dev/null 2>&1 || true

if [ "$DESACTIVAR_AUTOARRANQUE" = true ]; then
	rm -f "$ARCHIVO_AUTOARRANQUE"
	echo "Autoarranque desactivado: $ARCHIVO_AUTOARRANQUE"
elif [ "$INSTALAR_AUTOARRANQUE" = true ]; then
	mkdir -p "$RUTA_AUTOARRANQUE"
	cat > "$ARCHIVO_AUTOARRANQUE" <<EOF
[Desktop Entry]
Name=Estira las piernas
Comment=Recordatorio para levantarte cada cierto tiempo
Exec=python3 "$ARCHIVO_APP"
Icon=$RUTA_ICONO
Terminal=false
Type=Application
Categories=Utility;Health;
StartupNotify=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=10
EOF
	echo "Autoarranque activado: $ARCHIVO_AUTOARRANQUE"
fi

echo "Lanzador instalado en: $ARCHIVO_LANZADOR"
echo "Puedes abrirlo desde el menú de aplicaciones buscando: Estira las piernas"
echo ""
echo "Para desinstalar en el futuro:"
echo "  sh $RUTA_APP/install_desktop_entry.sh --desinstalar"
