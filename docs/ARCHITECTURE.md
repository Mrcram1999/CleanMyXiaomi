# Architecture

`PROMPT.md` is the conversational workflow; `AGENTS.md` governs agent behavior and contributions. The CLI provides stable JSON for the agent to translate and explain.

```text
User + agent → doctor/devices/detect → audit → approved profile → plan
                                                           ↓ human consent
                       durable intent ← cleanup ← exact hash + serial
                              ↓               ↓
                        local journal      verify state
                              ↓
                       restore preview → separate consent → exact-state restore
```

- `adb.py`: trusted executable discovery, bounded subprocess calls, shell argument validation, USB identity and package-state parsers.
- `policy.py`: closed profile registry, compatibility scope and protected components.
- `storage.py`: exclusive JSON writes, content hashes, device locks and append-only hash-chained journals with fsync.
- `engine.py`: read-only audit, plan validation, preflight checks, mutation sequence and recovery reconciliation.
- `__main__.py`: argument parsing, JSON reports, local device lock and error exits.

Only the engine calls state-changing package commands. The initial release does not support uninstall, app data changes, network ADB, UI automation, root or settings writes. `settings get` is used only to identify enabled keyboards during a future supported cleanup. There are no external runtime libraries or cloud APIs.

Plans include full inventory and exact original target state. Approval hashes bind reviewed content; they do not provide signatures. Cleanup is deliberately not atomic across packages: Android provides no such transaction here. A write-ahead intent makes partial execution inspectable and recoverable when ADB remains available. No automatic rollback is attempted after a failure because it is a separate change needing review.

Locking protects cooperative sessions of this tool, not unrelated processes. Firmware properties and versionCode cannot prove APK authenticity. Tests use synthetic responses at the ADB boundary, with subprocess behavior separately mocked; real-device integration remains a release gate.
