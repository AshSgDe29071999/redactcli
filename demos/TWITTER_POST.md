# Social post pack — redactcli

Assets (local):
- `demos/redactcli-demo.gif` (~176KB, autoplay-friendly)
- `demos/redactcli-demo.mp4` (~120KB, for X native video)
- `demos/redactcli-twitter-card.png` (static before/after)

Raw URLs after push:
- https://github.com/AshSgDe29071999/redactcli/raw/main/demos/redactcli-demo.gif
- https://github.com/AshSgDe29071999/redactcli/raw/main/demos/redactcli-demo.mp4
- https://github.com/AshSgDe29071999/redactcli/raw/main/demos/redactcli-twitter-card.png

---

## Tweet 1 (main post — paste this)

**Attach:** `redactcli-demo.gif` or `redactcli-demo.mp4` (prefer MP4 on X)

```
Your AI agent just dumped this into a log:

AWS_ACCESS_KEY_ID=AKIA…
GITHUB_TOKEN=ghp_…
postgres://user:password@db/prod
-----BEGIN RSA PRIVATE KEY-----

One pipe. Gone.

cat agent.log | redactcli

pip install redactcli

CLI + GitHub Action. Offline. Free. MIT.
https://github.com/AshSgDe29071999/redactcli
```

---

## Tweet 2 (reply / thread — social proof + how)

```
Why this exists:

Coding agents and CI love to echo secrets.
Humans then paste those logs into chat, PRs, and tickets.

redactcli is pipe-friendly on purpose:

• stdin → stdout (agent-native)
• `redactcli scan .` fails CI if secrets leak
• GitHub Action included
• zero runtime deps

PyPI: https://pypi.org/project/redactcli/
```

---

## Tweet 3 (hook for builders)

```
If you ship agents, drop this in CLAUDE.md / AGENTS.md:

"Before pasting logs or env dumps, run:
 cmd 2>&1 | redactcli"

One line. Fewer credential rotations. Happier security team.
```

---

## LinkedIn variant (longer)

```
Shipping coding agents without redaction is how AWS keys end up in Slack.

I published redactcli — a small offline CLI + GitHub Action that redacts high-signal secrets from agent logs, diffs, and CI output.

pip install redactcli
cat dump.log | redactcli
redactcli scan .

No cloud. No API key. MIT.
Repo: https://github.com/AshSgDe29071999/redactcli
PyPI: https://pypi.org/project/redactcli/
```

---

## Hashtags (use 1–2 max on X; more on LinkedIn)

`#devtools` `#AI` `#security` `#python` `#githubactions`
