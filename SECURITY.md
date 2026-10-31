# Security policy

This is an early alpha; no real-device cleanup profiles are approved in v0.1.0. Security-sensitive areas include package allowlisting, device identity, consent binding, shell argument handling, journal integrity and restore.

Please report exploitable safety bypasses privately using the repository's GitHub **Security → Report a vulnerability** option when enabled. If private reporting is unavailable, open a minimal issue requesting a private reporting channel without disclosing exploit details, serials, tokens or package inventories. No private support email is invented here.

Include affected version/commit, operating system, a synthetic reproducer, expected versus actual behavior and potential impact. Do not test destructive effects on someone else's phone. There is no promised response SLA; maintainers will triage according to impact and availability.

Only the latest release receives fixes. Keep the original trusted release and journal needed for recovery, but consult advisories before executing a version known to have a safety defect. The offline CLI sends no telemetry. AI tools have their own data handling policies.
