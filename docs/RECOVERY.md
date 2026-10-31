# Restauración y recuperación

**Si solo has hecho una auditoría con los perfiles incluidos, no necesitas restaurar nada: no se han cambiado paquetes.** Esta guía describe la recuperación de operaciones que llegue a realizar un perfil de limpieza verificado.

Conserva la versión original del proyecto, el plan y el registro antes de aplicar una limpieza. El registro incorpora el plan revisado y los estados originales de los paquetes. No contiene una copia de los APK, datos de aplicaciones, firmware ni archivos personales.

## Restauración normal

1. Reconecta el mismo teléfono por USB, desbloquéalo y utiliza el usuario principal 0. Deben mantenerse el firmware y las versiones de paquetes registrados. No utilices otro limpiador al mismo tiempo.
2. Ejecuta la previsualización. Sustituye el número de serie y la ruta por los de tu sesión; en Windows cambia `python3` por `py -3`:

```sh
python3 -m cleanmyxiaomi --serial TU_SERIAL_USB restore --journal sessions/limpieza.journal.jsonl
```

3. Revisa el teléfono, los paquetes, los estados originales y el SHA-256 mostrado. Una lista de acciones vacía significa que los paquetes intentados ya tienen su estado original registrado.
4. Solo después de aprobar ese plan de restauración, añade `--apply`, la huella completa y la confirmación del número de serie:

```sh
python3 -m cleanmyxiaomi --serial TU_SERIAL_USB restore --journal sessions/limpieza.journal.jsonl --apply --approve SHA256_COMPLETO_DE_RESTAURACION --confirm-device TU_SERIAL_USB
```

5. Comprueba manualmente las funciones del teléfono. Conserva el registro después de restaurar. Una nueva limpieza requiere otra auditoría, otro plan y otro registro.

El estado 0 —valor predeterminado de Android— se recupera con `pm default-state`; el estado 1 —activado explícitamente— con `pm enable`. El motor construye esos comandos con el paquete exacto registrado, actúa en orden inverso y comprueba cada resultado. No genera scripts ejecutables a partir de texto no fiable.

## Si se interrumpió una limpieza o restauración

**No repitas la limpieza.** Una entrada `intent` sin `applied` puede significar que el teléfono cambió antes de perder la conexión. La restauración consulta el estado real e incluye solo las operaciones intentadas cuyos paquetes siguen en el estado 3, desactivados para el usuario.

Si se interrumpió la propia restauración, previsualízala otra vez y aprueba el nuevo plan. Los paquetes ya restaurados se omiten.

Si queda un archivo de bloqueo tras cerrar un proceso por la fuerza, comprueba que no se está ejecutando ninguna sesión de CleanMyXiaomi y que nadie está gestionando el teléfono desde otro sitio antes de retirar únicamente el bloqueo de ese dispositivo. No elimines bloqueos como reintento automático.

## Cuándo se detiene la herramienta

- **Otro número de serie, identificador de arranque, firmware, usuario, versión de paquete o estado inesperado:** no edites el plan ni sus huellas para forzar la restauración. Conserva los datos originales y actuales de forma privada para revisarlos.
- **Registro ausente, dañado o incompleto:** conserva los bytes originales. No recortes, regeneres ni inventes el registro. Un revisor puede proponer una recuperación manual a partir del plan intacto y el estado confirmado, siempre con consentimiento explícito.
- **Registro de perfiles cambiado:** conserva la versión de confianza utilizada originalmente. Si un perfil fue retirado por seguridad, consulta el problema antes de ejecutar una versión antigua o saltarte controles.
- **ADB inaccesible o el teléfono no arranca:** esta herramienta no puede garantizar la recuperación. Recurre al soporte del fabricante. El proyecto no obtiene root, flashea ni restablece el móvil de fábrica.

Nunca actives todos los paquetes indiscriminadamente. No hay una alternativa automática de desinstalar/reinstalar ni se reinicia el móvil sin una decisión independiente del usuario. Revertir estados no equivale a recuperar una copia de seguridad completa.
