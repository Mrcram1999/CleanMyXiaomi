# Validation record — 0.1.0

Date: 2026-10-31.

- Local environment: macOS, CPython 3.14.7.
- 41 automated tests passed with `python3 -m unittest discover -s tests -v`.
- Offline repository checks passed: required files, registered profile hashes, audit-only release policy, local Markdown links and pinned GitHub Actions.
- Built and installed the package in a fresh virtual environment; `--version` and `profiles` worked from the installed package with isolated Python imports. Packaged profile data was present.
- Source ZIP was extracted into a clean directory; tests and repository checks were rerun from that extracted source.
- No real phone was connected or modified. No package profile has hardware approval. Tests use synthetic ADB responses and mock subprocess boundaries.
- GitHub CI is configured for Windows, macOS and Linux with Python 3.10 and 3.14. Configuration alone is not a claim that remote runs passed; inspect the actual Actions results for the published commit.

Hardware testing, OEM parser variations, phone functionality and power-loss recovery still require real-device validation. README status and the empty mutation registry make these limitations explicit.
