# Setup / Instalación

## English

1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/) or your trusted OS package manager. Open a terminal in the extracted repository. No runtime dependencies are required.
2. Run `python3 -m cleanmyxiaomi doctor`. This discovers ADB on PATH, in ANDROID_HOME / ANDROID_SDK_ROOT, or common Android SDK locations. `scripts/adb-guide.sh` and `scripts/adb-guide.ps1` only print help; they never install anything.
3. If needed, download **SDK Platform Tools** for your OS from [Google's official page](https://developer.android.com/tools/releases/platform-tools). Review the download/license yourself, extract to a folder you control, and add that folder to PATH or use the global `--adb` argument. Do not download a random “ADB installer,” pipe downloads into a shell, or run ADB as administrator/root.
4. macOS/Linux: use the extracted `platform-tools/adb`. Windows: use `platform-tools/adb.exe` and `py -3 -m cleanmyxiaomi` if `python3` is unavailable. On Windows, USB driver installation may be needed; use the device vendor's signed driver. On Linux, resolve USB group/udev access using your distribution's documentation instead of running this tool with sudo. Hardware access changes require the owner's review.
5. On the phone, open Settings → About phone. Depending on MIUI/HyperOS, tap the OS/version entry repeatedly until Developer options are enabled. Find Developer options (often under Additional settings) and enable **USB debugging**. Names vary. Do not enable OEM unlocking or extra Xiaomi security overrides for this tool.
6. Connect with a data-capable USB cable, unlock the phone and approve the computer's RSA debugging prompt only if this is a trusted computer. USB charging alone may not supply a data connection.
7. Run `devices`, then select the exact serial explicitly. `unauthorized`: approve on the phone. `offline`: reconnect and recheck. No device: try a data cable/port and review drivers. Do not guess the serial or choose the first listed device.

ADB may start its local background server during discovery; this is not a package change. Only the local default server and direct USB transport are supported. Unset ADB_SERVER_SOCKET, ANDROID_ADB_SERVER_PORT, ANDROID_ADB_SERVER_ADDRESS and ANDROID_SERIAL if configured. Read-only identity checks require owner user 0, non-root shell UID 2000 and boot serial properties. Unsupported or missing outputs stop the tool.

The tool intentionally does not install ADB automatically: host software installation and vendor license acceptance remain explicit user actions. An agent can guide or perform an authorized installation from a trusted source, but cannot silently accept terms.

## Español

Instala Python 3.10 o posterior y ejecuta `doctor` desde la carpeta del proyecto. Si falta ADB, descarga Android SDK Platform Tools desde la página oficial de Google enlazada arriba, revisa sus condiciones y extrae el archivo. Añade la carpeta a PATH o indica `--adb` antes del comando. En Windows puedes utilizar `py -3`.

En el teléfono, activa las opciones de desarrollador desde la versión del sistema en «Acerca del teléfono» y después activa «Depuración USB». Los nombres dependen de la versión. No actives el desbloqueo OEM ni opciones adicionales para saltarte restricciones de seguridad. Conecta un cable de datos, desbloquea el móvil y acepta la autorización del ordenador si confías en él.

Ejecuta `devices`, identifica tu número de serie y úsalo explícitamente. Si aparece `unauthorized`, falta autorizar en el móvil; si aparece `offline`, revisa la conexión. En Windows pueden hacer falta controladores oficiales; en Linux, permisos USB de tu distribución. No ejecutes la herramienta con root o como administrador para evitar estos controles.

Los scripts de ayuda no instalan nada. La instalación y sus condiciones requieren tu intervención o autorización específica. Al terminar, desactiva la depuración USB y revoca las autorizaciones si ya no las necesitas.
