<p align="center"><img src="docs/banner.svg" alt="CleanMyXiaomi — Tu móvil. Tú decides." width="960"></p>

<h1 align="center">CleanMyXiaomi</h1>
<p align="center"><strong>Tu móvil. Tú decides.</strong><br>Revisa tu Xiaomi · Redmi · POCO con ayuda de un agente de IA.</p>
<p align="center"><a href="#empieza-aquí">Empezar</a> · <a href="PROMPT.md">Instrucciones para el agente</a> · <a href="docs/RECOVERY.md">Restauración</a> · <a href="README.en.md">English</a></p>

**Estado actual: versión alfa. Ya puedes identificar el móvil, revisar las aplicaciones instaladas y generar una simulación. Todavía no hay perfiles de limpieza aprobados en teléfonos reales.** Los tres perfiles incluidos son de **solo auditoría**: no desactivan ni desinstalan aplicaciones.

El motor de desactivación reversible y restauración está implementado y tiene pruebas simuladas. Para habilitar cambios reales hace falta un perfil revisado y probado en el modelo, firmware, región y versiones de aplicaciones exactos. No se promete eliminar todos los anuncios.

## Empieza aquí

Puedes utilizarlo de dos maneras:

- **Con un agente de IA:** abre la carpeta del proyecto en tu agente y pega el texto del paso 4. Te guiará durante el proceso.
- **Manualmente:** sigue los comandos de los pasos 1 a 8. No necesitas una cuenta de IA para ejecutar la herramienta.

**No se instala una aplicación en el móvil.** El proyecto se ejecuta en tu ordenador y utiliza ADB para comunicarse con el teléfono por USB. No requiere root ni desbloquear el cargador de arranque.

## 1. Prepara lo necesario

- Un Xiaomi, Redmi o POCO tuyo, con MIUI o HyperOS y Android 8 o posterior.
- Un ordenador con Windows, macOS o Linux.
- Un cable USB que permita **transferir datos**, no solo cargar.
- **Python 3.10 o posterior** y **Android SDK Platform Tools**, que incluye ADB.
- Acceso al usuario principal del teléfono, el usuario 0; no a un usuario secundario.

Haz tu copia de seguridad habitual antes de plantearte cualquier modificación. El informe de esta herramienta **no es una copia de tus fotos, archivos o datos de aplicaciones**.

## 2. Descarga y abre el proyecto

En la parte superior de [este repositorio](https://github.com/Mrcram1999/CleanMyXiaomi), pulsa **Code → Download ZIP**. Descomprime el archivo: no ejecutes los comandos desde dentro del ZIP.

Abre una terminal **dentro de la carpeta que contiene `README.md`, `PROMPT.md` y `cleanmyxiaomi/`**. Por ejemplo, abre esa carpeta en tu editor y utiliza su terminal integrada. También puedes usar `cd "RUTA_DE_LA_CARPETA"`, sustituyendo el texto por la ruta real.

Comprueba Python:

| Windows — PowerShell o Terminal | macOS / Linux — Terminal |
| --- | --- |
| `py -3 --version` | `python3 --version` |

Si no está instalado, obtén Python desde [python.org](https://www.python.org/downloads/) o el gestor de paquetes de confianza de tu sistema. Si aparece una versión anterior a 3.10, actualízala antes de seguir.

## 3. Prepara el móvil y conecta el USB

1. Abre **Ajustes → Acerca del teléfono**.
2. Pulsa varias veces sobre la versión de MIUI/HyperOS o la información de compilación hasta que el teléfono indique que se han activado las opciones de desarrollador. La entrada concreta cambia según la versión.
3. Busca **Opciones de desarrollador**, normalmente dentro de **Ajustes adicionales**.
4. Activa **Depuración USB**. No actives «Desbloqueo OEM» ni opciones adicionales para saltarte restricciones de seguridad.
5. Conecta el móvil al ordenador con el cable de datos y desbloquea su pantalla.
6. Cuando aparezca el aviso para autorizar la depuración desde ese ordenador, acéptalo **solo si es tu ordenador de confianza**. Puede aparecer al ejecutar ADB en el siguiente paso.

Si no encuentras una opción, consulta la documentación de tu modelo o pide ayuda al agente. No cambies ajustes distintos por probar.

## 4. Elige: que te guíe un agente o seguir manualmente

### Con un agente de IA

Abre la carpeta del repositorio en tu agente de programación y pega este texto:

```text
Lee PROMPT.md y AGENTS.md y sigue su procedimiento.
Quiero auditar mi Xiaomi, Redmi o POCO. Respóndeme en castellano.
Pregúntame el modelo y si ya he activado la depuración USB.
Comprueba el teléfono conectado, explícame cada paso y guarda el informe.
No modifiques paquetes ni ajustes sin mostrarme el plan y recibir mi aprobación explícita.
Si no hay un perfil de limpieza verificado para mi dispositivo, limita el trabajo a la auditoría.
```

El agente debe ayudarte a preparar ADB, identificar el teléfono y explicar el resultado. Responde a sus preguntas y revisa lo que propone. **Pegar este texto no aprueba una limpieza.** La aprobación de cambios debe referirse a una lista concreta y al teléfono exacto.

El agente responde en el idioma que utilices y cambia si tú cambias. Los comandos y nombres de paquetes no se traducen. Los mensajes técnicos de la herramienta salen en inglés y el agente puede explicártelos en castellano.

### Si prefieres hacerlo tú

Continúa con los siguientes pasos. Los comandos de auditoría y simulación no modifican paquetes del móvil.

## 5. Comprueba ADB

| Windows | macOS / Linux |
| --- | --- |
| `py -3 -m cleanmyxiaomi doctor` | `python3 -m cleanmyxiaomi doctor` |

**Qué debe ocurrir:** verás la ruta y la versión de ADB si se ha encontrado. Si aparece `ADB not found`, descarga **SDK Platform Tools** para tu sistema desde [la página oficial de Google](https://developer.android.com/tools/releases/platform-tools), revisa sus condiciones y extrae el archivo.

Añade la carpeta `platform-tools` a PATH o indica la ruta de ADB en cada comando. Ejemplos con rutas que debes sustituir:

```powershell
# Windows
py -3 -m cleanmyxiaomi --adb "C:\ruta\platform-tools\adb.exe" devices
```

```sh
# macOS / Linux
python3 -m cleanmyxiaomi --adb "/ruta/platform-tools/adb" devices
```

`doctor` y los scripts `scripts/adb-guide.sh` y `scripts/adb-guide.ps1` **no instalan nada automáticamente**. No utilices instaladores ADB de origen desconocido ni ejecutes esta herramienta como administrador o con root. Más detalles: [instalación y conexión](docs/SETUP.md).

## 6. Identifica tu teléfono

| Windows | macOS / Linux |
| --- | --- |
| `py -3 -m cleanmyxiaomi devices` | `python3 -m cleanmyxiaomi devices` |

Busca el campo `serial` del móvil y comprueba que `state` sea `device`. Si hay varios dispositivos, identifica el tuyo: la herramienta no selecciona uno automáticamente.

**En todos los ejemplos siguientes sustituye `TU_SERIAL_USB` por ese número de serie real, sin añadir los signos `<` o `>`.** Si ADB no está en PATH, añade también `--adb` con su ruta antes del comando.

```powershell
# Windows
py -3 -m cleanmyxiaomi --serial TU_SERIAL_USB detect
```

```sh
# macOS / Linux
python3 -m cleanmyxiaomi --serial TU_SERIAL_USB detect
```

**Qué revisar:** fabricante, modelo, nombre interno del dispositivo, versión de Android, firmware y región si está disponible. Deben corresponder al móvil que tienes conectado. Si no coinciden o falta información requerida, detente; no edites los datos para forzar la comprobación.

## 7. Guarda una auditoría y genera la simulación

La auditoría guarda la identidad del teléfono y un inventario de aplicaciones en el ordenador. La simulación muestra las acciones autorizadas por el perfil.

```powershell
# Windows: ejecuta las líneas una a una
py -3 -m cleanmyxiaomi --serial TU_SERIAL_USB audit --out sessions/telefono.audit.json
py -3 -m cleanmyxiaomi profiles
py -3 -m cleanmyxiaomi --serial TU_SERIAL_USB plan --profile xiaomi-audit --out sessions/telefono.plan.json
py -3 -m cleanmyxiaomi dry-run --plan sessions/telefono.plan.json
```

```sh
# macOS / Linux: ejecuta las líneas una a una
python3 -m cleanmyxiaomi --serial TU_SERIAL_USB audit --out sessions/telefono.audit.json
python3 -m cleanmyxiaomi profiles
python3 -m cleanmyxiaomi --serial TU_SERIAL_USB plan --profile xiaomi-audit --out sessions/telefono.plan.json
python3 -m cleanmyxiaomi dry-run --plan sessions/telefono.plan.json
```

Puedes sustituir `xiaomi-audit` por `redmi-audit` o `poco-audit`. **Los tres son de solo auditoría y tienen el mismo alcance.** La carpeta `sessions/` se crea si no existe. Los archivos no se sobrescriben: para otra sesión utiliza nombres nuevos, por ejemplo `telefono-2.audit.json` y `telefono-2.plan.json`.

### Cómo interpretar el resultado

| Lo que aparece | Qué significa |
| --- | --- |
| `device` | Identidad del teléfono comprobado. |
| `inventory` | Aplicaciones instaladas, activadas y desactivadas. |
| `actions: []` | No hay cambios autorizados. **Es el resultado esperado con los perfiles incluidos.** |
| `skipped` | Elementos omitidos y sus motivos, si los hay. |
| `limitations` | Límites de lo que se ha podido comprobar. |
| `sha256` | Huella del contenido del plan; no es una autorización por sí sola. |

**Si el plan está vacío, has terminado la auditoría. No necesitas ejecutar `cleanup`.** No añadas paquetes manualmente ni copies listas genéricas para conseguir que aparezcan acciones.

## 8. Termina y guarda el resultado

Conserva tus informes en `sessions/`. Contienen identificadores del teléfono y aplicaciones instaladas: no los publiques en GitHub ni los pegues completos en una incidencia. Si usas un agente de IA, revisa qué datos compartes con ese servicio.

La auditoría no necesita restauración porque no ha cambiado paquetes. Si ya no vas a utilizar ADB, desactiva **Depuración USB** y revoca las autorizaciones del ordenador desde las opciones de desarrollador.

Para revisar manualmente opciones de publicidad de tu versión, consulta [la guía de ajustes](docs/ADS.md). Desactivar la personalización de anuncios no garantiza reducir su número.

## Problemas frecuentes

| Problema | Qué hacer |
| --- | --- |
| `python3` o `py` no se reconoce | Comprueba la instalación de Python y abre una terminal nueva. En Windows prueba `py -3`. |
| `No module named cleanmyxiaomi` | Abre la terminal en la carpeta extraída que contiene `cleanmyxiaomi/`. |
| `ADB not found` | Instala Platform Tools desde Google y añade su carpeta a PATH o usa `--adb`. |
| No aparece ningún dispositivo | Desbloquea el móvil, revisa la depuración USB y prueba un cable o puerto de datos. En Windows puede hacer falta el controlador oficial del fabricante. |
| `unauthorized` | Revisa y acepta en el móvil el aviso del ordenador de confianza; vuelve a ejecutar `devices`. |
| `offline` | Reconecta el cable y vuelve a comprobar el estado. No continúes mientras siga desconectado. |
| Ya existe el archivo de salida | Elige un nombre nuevo; la herramienta protege los informes anteriores. |
| No coincide el modelo, firmware o usuario | Detente y revisa la conexión y el usuario principal. No alteres el plan para saltarte la comprobación. |
| `actions: []` | Es normal en esta versión: no hay perfiles aprobados para modificar paquetes. |

## Limpieza y restauración: para futuros perfiles verificados

**Esta sección describe el motor disponible, pero no es un paso necesario ni una invitación a modificar el móvil con los perfiles actuales.** Un perfil de limpieza necesita pruebas reales y revisión según [la política de perfiles](docs/PROFILES.md).

Cuando exista uno compatible, el flujo será: auditoría nueva → plan exacto → explicación de efectos secundarios → aprobación explícita → registro de cada cambio → comprobación. Solo se admite la desactivación reversible por usuario, sin desinstalar ni borrar datos.

Estos ejemplos usan `python3`; en Windows sustitúyelo por `py -3`. Sustituye también el número de serie y las huellas por los valores del plan revisado:

```sh
# Solo tras aprobar expresamente un plan no vacío y verificado
python3 -m cleanmyxiaomi --serial TU_SERIAL_USB cleanup --plan sessions/telefono.plan.json --journal sessions/limpieza.journal.jsonl --approve SHA256_COMPLETO_DEL_PLAN --confirm-device TU_SERIAL_USB

# Primero previsualiza la restauración: este comando no modifica el móvil
python3 -m cleanmyxiaomi --serial TU_SERIAL_USB restore --journal sessions/limpieza.journal.jsonl --out sessions/restauracion.plan.json

# Solo tras aprobar por separado el plan de restauración
python3 -m cleanmyxiaomi --serial TU_SERIAL_USB restore --journal sessions/limpieza.journal.jsonl --apply --approve SHA256_COMPLETO_DE_RESTAURACION --confirm-device TU_SERIAL_USB
```

Conserva el registro y la versión original del proyecto. La restauración intenta devolver únicamente los paquetes registrados a su estado original; no activa todas las aplicaciones desactivadas. Si hubo una interrupción, no repitas la limpieza: consulta [la guía de recuperación](docs/RECOVERY.md).

## Seguridad, pruebas y contribuciones

- Sin root, desinstalaciones, borrado de datos, flasheo ni cambios silenciosos. No se admite ADB por Wi-Fi ni usuarios secundarios.
- Un paquete desconocido o una versión no verificada no se modifica. Las huellas detectan cambios del contenido; no protegen frente a un código fuente manipulado maliciosamente.
- Los planes caducan a las 24 horas. Cambiar el dispositivo, firmware, inventario o estado de un objetivo exige una nueva revisión. Una actualización también puede impedir la restauración automática.
- La reversión de estados no garantiza recuperar un teléfono ante cualquier fallo. ADB no demuestra que llamadas, SMS, datos móviles, cámara, notificaciones, cuentas y actualizaciones funcionen: esas comprobaciones requieren el teléfono real.
- La herramienta no envía telemetría. Tu agente de IA tiene sus propias condiciones de tratamiento de datos.

Para comprobar el proyecto desde su carpeta:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
python3 scripts/build_release.py
```

En Windows utiliza `py -3`. No hay dependencias externas durante la ejecución. La instalación como paquete Python es opcional: los pasos anteriores funcionan directamente desde la carpeta extraída.

Consulta [la seguridad](docs/SAFETY.md), [las contribuciones](CONTRIBUTING.md), [la política de vulnerabilidades](SECURITY.md) y [la validación](docs/VALIDATION.md). Parte de la documentación técnica para desarrolladores está en inglés. Las pruebas simuladas no equivalen a certificar la compatibilidad de un teléfono real.
