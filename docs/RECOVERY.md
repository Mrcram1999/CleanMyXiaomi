# Restore / Restauración

Preserve the original checkout, plan and journal on your computer before cleanup. The journal embeds the reviewed plan and original target states. It is a state snapshot, not an APK, user-data, firmware or personal-file backup.

## Normal path

1. Reconnect the same phone by USB, unlock it and use owner user 0. Keep the same firmware and package versions. Do not run another cleaner.
2. Run `python3 -m cleanmyxiaomi --serial YOUR_USB_SERIAL restore --journal sessions/cleanup.journal.jsonl`.
3. Review the displayed device, packages, original states and restore SHA-256. An empty action list means the attempted packages already have their recorded original states.
4. After explicit approval, rerun with `--apply --approve FULL_RESTORE_SHA256 --confirm-device YOUR_USB_SERIAL`.
5. Verify phone functions manually. Preserve the journal after restoration; a new cleanup uses a new audit, plan and journal.

Default state 0 is restored using `pm default-state`; explicit state 1 uses `pm enable`. Those commands are built internally with the recorded exact package; the tool does not generate an executable restore script from untrusted text. It restores in reverse order and verifies each result.

## Interrupted cleanup or restore

Do not rerun cleanup. An `intent` without an `applied` entry may mean the phone changed before the connection failed. Restore inspects the live state and includes only attempted entries still in disabled-user state 3. It does not assume a failed command made no change. If restore itself was interrupted, preview it again and approve the new preview; already-restored states are skipped.

A leftover lock after a killed process is conservative. Verify that no CleanMyXiaomi process is active and the phone is not being managed elsewhere before removing only that device's lock file. Do not remove locks as an automatic retry strategy.

## Refusals and hard limits

- Different serial, boot serial, build, owner user, package version or an unexpected target state: stop. Do not edit identity fields or hashes to force restoration. Gather the original and current state privately for a device-specific review.
- Missing, corrupt or truncated journal: keep the original bytes. Do not auto-truncate, regenerate or fabricate a journal. A reviewer may use the intact plan and confirmed live state to propose manual recovery; explicit user consent still applies.
- Changed profile registry: keep the trusted release used for the operation. Routine upgrades must not discard historical recovery material. If a profile was revoked for safety reasons, seek review instead of bypassing it.
- ADB unavailable or phone not booting: this tool cannot promise recovery. Use the manufacturer's support process. No rooting, flashing or factory reset is performed by this project.
- No blanket `pm enable` loops; no automatic uninstall/install fallback; no reboot without a separate user decision.

## Español

Conserva el plan, el registro y la versión original del proyecto. Reconecta el mismo teléfono, con el mismo firmware y usuario principal. `restore` muestra primero una simulación; solo cambia el móvil al añadir `--apply` y aprobar la huella de esa restauración.

Si hubo una desconexión, no repitas la limpieza: consulta la restauración. La herramienta comprueba qué operaciones llegaron a aplicarse, incluidas aquellas cuyo resultado no pudo registrarse. Si el registro está dañado, falta ADB o cambió el firmware, se detiene. No edites los datos para forzarla. La reversión de estados no es una copia de seguridad completa ni una garantía de recuperación del teléfono.
