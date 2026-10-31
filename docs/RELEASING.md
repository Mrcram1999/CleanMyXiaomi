# Release checklist

- Run the tests and repository checks on the supported CI matrix. Review every workflow change.
- Verify README parity, version metadata and changelog. Preserve the clear early-alpha/hardware-support limitation.
- Review approved profile hashes and evidence. Never add a mutation profile without real-device validation and independent human review.
- Build with `python3 scripts/build_release.py`; inspect the ZIP manifest. It must not contain sessions, credentials, bytecode, caches, .git or synthetic test-generated profile registries.
- Test the ZIP in a clean folder and run the CLI's `--help`, `profiles` and test suite. Optionally build/install the wheel in a fresh virtual environment and check bundled data.
- Review GitHub Actions results; pin actions by full commit and keep dependency updates reviewed.
- Create a tag only after review. The release workflow builds downloadable artifacts; it does **not** publish a GitHub Release or PyPI package automatically.
- If publishing a release, include the checksum, support limitations, actual tested environments and recovery notes. Enable private vulnerability reporting in repository settings if available.
