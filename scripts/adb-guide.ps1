# Guidance only: no installation, downloads or device changes.
$ErrorActionPreference = 'Stop'
Write-Output 'CleanMyXiaomi: ADB setup / Instalación de ADB'
Write-Output 'https://developer.android.com/tools/releases/platform-tools'
Write-Output 'Extract Platform Tools and add its folder to PATH, or use --adb C:\path\platform-tools\adb.exe'
Write-Output 'Extrae Platform Tools y añade su carpeta a PATH. Consulta docs/SETUP.md.'
Write-Output 'No software has been installed / No se ha instalado software.'
$adbCommand = Get-Command adb -ErrorAction SilentlyContinue
if ($adbCommand) { Write-Output $adbCommand.Source }
