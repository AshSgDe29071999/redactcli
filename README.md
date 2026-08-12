# redactcli

**Stop agents and CI from leaking live secrets.** Pipe-friendly CLI + GitHub Action. No cloud. No API key.

```bash
# try — no install
uvx redactcli --help
npx --yes github:AshSgDe29071999/redactcli --help

# pipe agent / CI logs
echo 'token=ghp_…' | uvx redactcli
```

[![PyPI](https://img.shields.io/pypi/v/redactcli.svg)](https://pypi.org/project/redactcli/)
[![Python](https://img.shields.io/pypi/pyversions/redactcli.svg)](https://pypi.org/project/redactcli/)

Designed for humans **and** coding agents.

---

## Why

Agents and CI constantly echo AWS keys, GitHub / GitLab / npm / PyPI tokens, private keys, database URLs with passwords, JWTs, and Slack/Stripe keys.

`redactcli` strips those **before** logs leave your machine or a PR is merged.

---

## Install

### Homebrew

```bash
brew tap ashsgde29071999/redactcli
brew install redactcli
```

### Binary (no Python)

Download the file for your OS from [Releases](https://github.com/AshSgDe29071999/redactcli/releases), `chmod +x`, put it on `PATH`.

```bash
# Linux x86_64 example
curl -fsSL -o redactcli \
  https://github.com/AshSgDe29071999/redactcli/releases/latest/download/redactcli-linux-x86_64
chmod +x redactcli && ./redactcli --version
```

Or build one locally: `scripts/build-binary.sh` (PyInstaller).

### uv / pipx / pip

```bash
uvx redactcli --help
pipx install redactcli
pip install redactcli
```

Requires **Python 3.10+**. Zero runtime dependencies.

---

## CLI

### `redact` (default)

Read stdin and/or files; write redacted text to stdout.

```bash
echo 'token=ghp_…' | redactcli
redactcli redact ./dump.txt
redactcli redact -i ./notes.md          # in place
redactcli redact ./a.log -o ./a.clean
redactcli redact --json < dump.txt      # for agents
```

### `scan`

Report findings without rewriting. Exit code **1** if anything matched (CI-friendly).

```bash
redactcli scan .
redactcli scan --json src/
redactcli scan --no-fail-on-findings .
```

### `patterns`

```bash
redactcli patterns
redactcli patterns --json
```

### Options

| Flag | Meaning |
|------|---------|
| `--rules FILE` | Extra patterns (JSON) |
| `--include NAME` | Only these built-ins (repeatable) |
| `--exclude NAME` | Skip these built-ins (repeatable) |
| `--min-confidence high\|medium` | Default `medium` |
| `--json` | Machine-readable output |

---

## pre-commit

Put this **above** other hooks so a leaked token never lands in git.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/AshSgDe29071999/redactcli
    rev: v0.1.1
    hooks:
      - id: redactcli
```

```bash
pre-commit install
git add . && git commit -m "test"
```

---

## GitLab CI

```yaml
# .gitlab-ci.yml
include:
  - remote: https://raw.githubusercontent.com/AshSgDe29071999/redactcli/v0.1.1/templates/gitlab-ci.yml
```

Override paths or confidence with `REDACTCLI_PATHS` and `REDACTCLI_MIN_CONFIDENCE`.

---

## GitHub Action

Fails the check when the diff or workspace contains secrets — the Marketplace listing uses this GIF:

![Failed PR: redactcli Secret Scan](demos/redactcli-failed-pr.gif)

```yaml
# .github/workflows/secret-scan.yml
name: Secret scan
on:
  pull_request:
  push:
    branches: [main]

jobs:
  redactcli:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: AshSgDe29071999/redactcli@v0.1.1
        with:
          scan-mode: git-diff
          min-confidence: medium
          fail-on-findings: true
```

`uses: AshSgDe29071999/redactcli/action@v0.1.1` still works.

### Action inputs

| Input | Default | Description |
|------|---------|-------------|
| `scan-mode` | `workspace` | `workspace` or `git-diff` |
| `paths` | `.` | Paths to scan (workspace mode) |
| `min-confidence` | `medium` | `high` or `medium` |
| `fail-on-findings` | `true` | Fail job on secrets |
| `python-version` | `3.12` | Runner Python |
| `version` | latest | Pin PyPI version |

To list this Action on the GitHub Marketplace: open the `v0.1.1` release → **Publish this Action to the GitHub Marketplace** → category *Security* / *Continuous integration*. Use `demos/redactcli-failed-pr.gif` as the listing image.

---

## Built-in detections (high signal)

- PEM / OpenSSH private keys
- AWS access key ids (`AKIA…` / `ASIA…`)
- AWS secret keys near assignment keywords
- GitHub tokens (`ghp_`, `github_pat_`, …)
- GitLab (`glpat-`), Slack, Stripe, OpenAI, Anthropic
- PyPI / npm tokens
- JWTs
- DB / HTTP URLs with embedded credentials
- Common `api_key=` / `password=` assignments
- Google API keys, Azure AccountKey

Use `redactcli patterns` for the full list.

---

## Custom rules

`rules.json`:

```json
{
  "patterns": [
    {
      "name": "acme_token",
      "description": "Acme internal token",
      "regex": "\\bACME_[A-Z0-9]{16}\\b",
      "replacement": "[REDACTED:ACME_TOKEN]",
      "confidence": "high"
    }
  ]
}
```

```bash
redactcli scan --rules rules.json .
```

---

## Library use

```python
from redactcli import redact_text, scan_text

result = redact_text(open("log.txt").read())
print(result.text)
print(result.count, "findings")

for f in scan_text("AKIAIOSFODNN7EXAMPLE"):
    print(f.pattern, f.line, f.excerpt)
```

---

## Agent / `CLAUDE.md` snippet

```text
Before pasting logs or env dumps into chat or commits, run:
  redactcli redact < file
  # or
  cmd 2>&1 | redactcli
```

---

## Development

```bash
git clone https://github.com/AshSgDe29071999/redactcli.git
cd redactcli
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
ruff check src tests
```

---

## Security notes

- Patterns aim for **high precision**; no tool catches everything.
- Prefer `--min-confidence high` in noisy monorepos.
- Rotate any secret that ever appeared unredacted in logs or chat.
- This package **does not** send data anywhere.

---

## License

MIT — see [LICENSE](LICENSE).
