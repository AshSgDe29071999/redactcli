# Changelog

## 0.1.0 — 2026-08-05

### Added
- Core secret redaction engine with built-in high-signal patterns
- CLI: `redact` (stdin/files), `scan` (report + exit code), `patterns`
- Custom rules via YAML/JSON (`--rules`)
- JSON output for agents (`--json`)
- GitHub Action for PR / workspace secret scanning
- Unit tests for patterns, engine, and CLI
