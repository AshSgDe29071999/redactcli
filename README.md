# redactcli

**Redact secrets from agent output, logs, diffs, and CI.**

Pipe-friendly CLI + GitHub Action. No cloud. No API key. Designed for humans **and** coding agents.

```bash
pip install redactcli

# Pipe agent / CI logs
cat agent.log | redactcli

# Scan a tree; exit 1 if secrets found
redactcli scan src/ .env.example

# Rewrite a file in place
redactcli redact -i ./notes.md
```

[![PyPI](https://img.shields.io/pypi/v/redactcli.svg)](https://pypi.org/project/redactcli/)
[![Python](https://img.shields.io/pypi/pyversions/redactcli.svg)](https://pypi.org/project/redactcli/)

---

## Why

Agents and CI constantly echo:

- AWS keys
- GitHub / GitLab / npm / PyPI tokens
- Private keys
- Database URLs with passwords
- JWTs and Slack/Stripe keys

`redactcli` strips those **before** logs leave your machine or a PR is merged.

---



## Demo

![redactcli demo](demos/redactcli-demo.gif)

*Stakes → agent dump → one pipe → CI blocks the PR.*

## Install

```bash
pip install redactcli
# or one-shot
uvx redactcli --help
```

Requires **Python 3.10+**. Zero runtime dependencies.

---

## CLI

### `redact` (default)

Read stdin and/or files; write redacted text to stdout.

```bash
# stdin
echo 'token=ghp_…' | redactcli
echo 'token=ghp_…' | redactcli redact

# files
redactcli redact ./dump.txt
redactcli redact -i ./dump.txt          # in place
redactcli redact ./a.log -o ./a.clean   # to file

# JSON for agents
redactcli redact --json < dump.txt
```

### `scan`

Report findings without rewriting. Exit code **1** if anything matched (CI-friendly).

```bash
redactcli scan .
redactcli scan --json src/
redactcli scan --no-fail-on-findings .   # report only
```

### `patterns`

List built-in rules.

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

## GitHub Action

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
      - uses: AshSgDe29071999/redactcli/action@v0.1.0
        with:
          paths: .
          min-confidence: medium
          fail-on-findings: true
```

Or pin to a commit SHA after release.

### Action inputs

| Input | Default | Description |
|-------|---------|-------------|
| `paths` | `.` | Paths to scan |
| `min-confidence` | `medium` | `high` or `medium` |
| `fail-on-findings` | `true` | Fail job on secrets |
| `python-version` | `3.12` | Runner Python |
| `version` | latest | Pin PyPI version |

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
