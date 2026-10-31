# Instalación y conexión

La [guía principal](../README.md) explica el recorrido completo con comandos para Windows, macOS y Linux. Aquí tienes los detalles de preparación.

## 1. Instala Python

Necesitas Python 3.10 o posterior, disponible en [python.org](https://www.python.org/downloads/) o en el gestor de paquetes de confianza de tu sistema. Abre una terminal en la carpeta extraída del proyecto, donde están `README.md` y `cleanmyxiaomi/`.

Comprueba `python3 --version` en macOS/Linux o `py -3 --version` en Windows. No hace falta instalar dependencias externas para ejecutar la herramienta desde esa carpeta.

## 2. Localiza o instala ADB

Ejecuta `python3 -m cleanmyxiaomi doctor`; en Windows, `py -3 -m cleanmyxiaomi doctor`.

El programa busca ADB en PATH, en ANDROID_HOME o ANDROID_SDK_ROOT y en ubicaciones habituales del SDK de Android. Los scripts `scripts/adb-guide.sh` y `scripts/adb-guide.ps1` solo muestran ayuda: no instalan ni descargan nada.

Si falta ADB:

1. Abre la [página oficial de Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools).
2. Selecciona la descarga para tu sistema y revisa tú mismo sus condiciones.
3. Extrae el archivo en una carpeta que controles.
4. Añade `platform-tools` a PATH o utiliza `--adb` con la ruta completa en cada comando. Ese argumento va antes del comando de la herramienta.

Ejemplos con rutas que debes sustituir:

```powershell
py -3 -m cleanmyxiaomi --adb "C:\ruta\platform-tools\adb.exe" devices
```

```sh
python3 -m cleanmyxiaomi --adb "/ruta/platform-tools/adb" devices
```

No descargues instaladores ADB de origen desconocido ni ejecutes descargas directamente como scripts. No ejecutes ADB ni este proyecto como administrador o con root para eludir permisos.

En Windows puede ser necesario instalar un controlador USB firmado del fabricante. En Linux, consulta los grupos y reglas USB de tu distribución. Cualquier cambio de permisos del ordenador debe revisarlo su propietario.

## 3. Activa la depuración USB

En el teléfono, abre **Ajustes → Acerca del teléfono**. Pulsa repetidamente la entrada de versión del sistema o compilación que corresponda a tu versión de MIUI/HyperOS hasta activar las opciones de desarrollador.

Busca **Opciones de desarrollador**, a menudo en **Ajustes adicionales**, y activa **Depuración USB**. Los nombres varían. No actives «Desbloqueo OEM» ni otras excepciones de seguridad para utilizar esta herramienta.

Conecta un cable USB de datos, desbloquea la pantalla y acepta el aviso de autorización RSA solo si confías en ese ordenador. Que el móvil cargue no demuestra que el cable permita transmitir datos. El aviso puede aparecer cuando ejecutes ADB.

## 4. Comprueba la conexión

Ejecuta `devices`, identifica tu número de serie y utilízalo explícitamente con `--serial`. Si aparecen varios móviles, no elijas uno por su posición en la lista.

| Estado | Acción |
| --- | --- |
| `device` | La conexión está autorizada; continúa con `detect` y verifica el modelo real. |
| `unauthorized` | Autoriza el ordenador en la pantalla del móvil y repite la comprobación. |
| `offline` | Reconecta y comprueba de nuevo antes de continuar. |
| Lista vacía | Revisa cable, puerto, depuración y controladores. |

ADB puede iniciar su servidor local en segundo plano durante la comprobación. Esto no modifica paquetes del móvil. Solo se admite el servidor local predeterminado y una conexión USB directa.

Si tienes configuradas ADB_SERVER_SOCKET, ANDROID_ADB_SERVER_PORT, ANDROID_ADB_SERVER_ADDRESS o ANDROID_SERIAL, revisa y elimina esas variables de esta sesión antes de utilizar la herramienta. La comprobación exige el usuario principal 0, una sesión ADB normal sin root —UID 2000— y los identificadores requeridos del teléfono. Si faltan datos o no se reconoce la salida, se detiene.

## 5. Al terminar

Guarda los informes de forma privada. Si ya no necesitas ADB, desactiva la depuración USB y revoca las autorizaciones del ordenador desde las opciones de desarrollador.

La instalación de software y la aceptación de licencias son acciones explícitas del usuario. Un agente puede orientar o instalar desde una fuente de confianza si está autorizado, pero no debe aceptar condiciones silenciosamente.
