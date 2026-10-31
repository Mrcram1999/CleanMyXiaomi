# Safety and threat model

The threat model covers accidental device selection, unreviewed package targets, stale plans, shell injection, partial failure, incorrect enabled-state restoration and accidental report publication. It does not defend against malicious local code, a compromised computer/ADB binary, falsified firmware properties, hostile same-user processes, forged hardware evidence or an agent that ignores these instructions.

## Enforced boundaries

- Explicit serial on every device-targeted call; direct USB transport only; shell UID 2000 and current user 0 required.
- Exact serial, boot serial, brand, manufacturer, model, codename, fingerprint, incremental build, Android/API version, MIUI/HyperOS property and available region bound into the plan. Missing required identity fails closed. Properties are not hardware attestation.
- Only a hash-registered approved profile. Device-tested profiles have an exact firmware scope, exact package version codes, evidence, side effects and a reviewer. Neither a JSON schema nor an AI assertion proves safety: maintainers must verify the evidence.
- Protected name families plus active launcher and enabled keyboard checks. The denylist is defense in depth; it is not exhaustive. Unknown packages cannot be targeted because they are absent from the allowlist.
- Only `disable-user --user 0`, `default-state --user 0` and `enable --user 0` mutations. No uninstall or data deletion implementation.
- Plan approval uses a full content hash and explicit serial confirmation. The agent obtains actual human consent before supplying these values. The CLI cannot prove that an AI received consent; possession of a hash alone is not human authorization.
- Preflight checks all target versions/states before the first mutation. Rechecks device identity and package state around each operation; unexpected inventory drift stops cleanup.
- Journals are created exclusively. Every mutation has a flushed/fsynced intent first; a missing success record is treated as possibly applied.
- A per-device lock in `~/.cleanmyxiaomi/locks` coordinates this tool's sessions across checkouts. It cannot lock Android Settings, other computers or unrelated ADB clients. Do not use concurrent device-management tools.
- Restore only touches attempted entries, in reverse order, and preserves Android state 0 (manifest default) versus 1 (explicit enabled). Already-disabled packages are skipped and never blanket-enabled.

## Integrity and privacy

SHA-256 envelopes and journal hash chains detect accidental corruption. They are **not signatures** and do not prevent malicious rewriting, valid-tail truncation or rollback of a file. Keep a trusted local copy of the checkout and recovery records. Review repository diffs before running code; no downloaded profiles are executed.

Reports contain serials, firmware metadata and installed application lists. New files use mode 0600 where the OS enforces POSIX permissions; Windows users must use a private directory with appropriate ACLs. Reports are ignored by Git only under the documented names/paths. Do not upload raw reports to public issues. No photos, contacts, messages, app-data backups or account credentials are read. No telemetry is sent by this CLI.

## Operational limits

Package-state rollback is not a guarantee that a phone can be recovered from every failure. A disabled component may prevent normal boot or ADB access. ADB verification cannot test calls, mobile data, background notifications, OTA or account workflows. Firmware updates can change package identities and restoration behavior. Power loss can damage the last journal entry; see RECOVERY.md.

No real device was connected or modified during development of v0.1.0. Bundled profiles are audit-only. Real-device testing and maintainer review are a release gate for any future mutation profile.
