#!/bin/sh
# Guidance only. No downloads, package manager calls or device modifications.
set -eu
printf '%s\n' 'CleanMyXiaomi: ADB setup / Instalación de ADB' \
  'Official download / Descarga oficial:' \
  'https://developer.android.com/tools/releases/platform-tools' \
  'Extract Platform Tools and add its folder to PATH, or use --adb /absolute/path/to/adb.' \
  'Extrae Platform Tools y añade su carpeta a PATH, o usa --adb /ruta/absoluta/adb.' \
  'Review docs/SETUP.md. No software has been installed / No se ha instalado software.'
if command -v adb >/dev/null 2>&1; then
  printf 'ADB found / ADB encontrado: '
  command -v adb
fi
