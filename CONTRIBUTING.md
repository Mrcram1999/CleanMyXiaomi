# Contributing

Small, reviewable contributions are welcome: parser compatibility, recovery reliability, documentation, translations and evidence-backed device profiles. Discuss behavior changes in an issue before broad refactors.

1. Fork the repository and create a branch. Use Python 3.10+; the CLI runs from the checkout without installation.
2. Keep runtime dependencies at zero unless there is a compelling reviewed need. Never introduce shell interpolation or automatic host/device mutations.
3. Add meaningful tests for parser variants, safety boundaries and partial failure. Use synthetic identifiers; never commit real serials, inventories or private logs.
4. Run `python3 -m unittest discover -s tests -v` and `python3 scripts/check_repository.py`.
5. Update both READMEs when user behavior changes. Keep the agent language-adaptive.
6. In the PR explain the concrete problem, resulting behavior, validation and limitations. Do not label synthetic tests as hardware support.

Device profiles follow [docs/PROFILES.md](docs/PROFILES.md), including real-device restore evidence and independent human review. The author must not approve their own mutation profile. Unknown packages stay unsupported. A schema-valid document is not an approved profile.

Respectful technical disagreement is welcome. Harassment, doxxing, spam and unsafe advice that bypasses consent are not. Maintainers may remove abusive content or close unsupported proposals. Contributions are provided under the project's MIT license; ensure you have the right to submit them.

**Español:** se aceptan mejoras pequeñas y verificables, documentación y perfiles respaldados por pruebas reales. Ejecuta las pruebas, explica los límites y no publiques datos privados del móvil. Nunca inventes compatibilidad ni elimines los controles de seguridad para hacer pasar una prueba.
