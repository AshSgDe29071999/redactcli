# Changelog

## 0.1.1 — 2026-08-12

### Added
- Root `action.yml` so the Action is Marketplace-listable (`uses: AshSgDe29071999/redactcli@v0.1.1`)
- `scan-mode: git-diff` input for PR-only scans
- Official pre-commit hook (`.pre-commit-hooks.yaml`)
- GitLab CI include template (`templates/gitlab-ci.yml`)
- One-file binaries via PyInstaller (`scripts/build-binary.sh`, `release-binaries` workflow)
- Homebrew tap formula (`ashsgde29071999/redactcli`)
- `npx --yes github:AshSgDe29071999/redactcli` launcher (`npm/cli.js`)
- Marketplace GIF of a failed secret-scan check (`demos/redactcli-failed-pr.gif`)

## 0.1.0 — 2026-08-05

### Added
- Core secret redaction engine with built-in high-signal patterns
- CLI: `redact` (stdin/files), `scan` (report + exit code), `patterns`
- Custom rules via YAML/JSON (`--rules`)
- JSON output for agents (`--json`)
- GitHub Action for PR / workspace secret scanning
- Unit tests for patterns, engine, and CLI
