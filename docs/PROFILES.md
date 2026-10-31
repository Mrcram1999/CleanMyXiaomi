# Profile review policy

The authoritative runtime registry is `cleanmyxiaomi/data/registry.json`; the JSON files live in `cleanmyxiaomi/data/profiles/`. No arbitrary profile path or remote profile URL is accepted by cleanup. The three shipped profiles have status `approved-audit-only`, empty scope and empty package lists. Their approval is for zero mutations, not for hardware compatibility.

A nonempty profile requires `approved-device-tested` and must pass `validate_profile` in `policy.py`. Schema validation is necessary but **does not grant approval**. Never change the registry to make an individual cleanup session proceed.

## Adding support

1. Open a profile proposal with exact manufacturer, brand, model, codename, build fingerprint, incremental build, Android release/API, MIUI/HyperOS values and available region. Remove serials and personal data from public evidence.
2. Research each package's actual role and dependencies. Record the exact package name, versionCode, purpose, expected benefit, side effects and a package-specific evidence URL. No wildcards, fuzzy model matches or broad “safe Xiaomi packages” claims.
3. A qualified volunteer must test on their own recoverable matching device under a separately reviewed test procedure. The production cleaner does not bypass its registry for experimentation. Do not ask an AI agent to invent test evidence or use fixtures on a phone.
4. Record pre/post states, confirmed effects, recovery to original states and checks for boot, calls, SMS, Wi-Fi, mobile data, camera, notifications, updates and accounts. Include how long background behavior was observed. An ADB success response is insufficient.
5. A maintainer reviews evidence and the independent risk assessment. Require a second human review for mutation profiles. Document reviewer, test date, evidence URL, `restore_verified: true` and the required essential-check names.
6. Add the reviewed JSON and its exact byte SHA-256 to the registry in the same PR. Test `python3 -m cleanmyxiaomi validate-profile PATH`, the full suite and repository checks. Review the diff and release notes. No self-approval during an end-user cleanup session.

Required top-level fields: `schema` (1), `id`, `status`, `description`, `scope`, `packages`, `review`. The executable validator in `policy.py` is the source of truth. See synthetic examples in tests only for field structure; their `example.invalid` evidence and identities are deliberately fictitious and must never be promoted.

Package versions and firmware scopes intentionally favor false negatives. After an OTA or app update, obtain fresh evidence and create a separately reviewed profile. Preserve historical trusted releases for recovery, and document any safety revocation prominently.

No device-specific removal candidates are shipped: there is no model-specific verification available for this initial release. Contributions that only quote a generic debloat list will not be accepted as proof.
