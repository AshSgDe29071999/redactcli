# Social post pack — redactcli (v2)

## Assets

| File | Use |
|------|-----|
| `demos/redactcli-demo.mp4` | **Prefer on X** (~16s, 226KB) |
| `demos/redactcli-demo.gif` | Autoplay fallback (~16s, 294KB) |
| `demos/redactcli-twitter-card.png` | Static 1200×675 |

GitHub:
- https://github.com/AshSgDe29071999/redactcli/raw/main/demos/redactcli-demo.mp4
- https://github.com/AshSgDe29071999/redactcli/raw/main/demos/redactcli-demo.gif
- https://github.com/AshSgDe29071999/redactcli/raw/main/demos/redactcli-twitter-card.png

### Story beats in the video
1. **Stakes** — about to paste agent logs / open PR  
2. **Dump** — realistic secret lines (fake only)  
3. **Fix** — `cat log \| redactcli`  
4. **CI** — `redactcli scan` → exit 1 / Action FAILED  
5. **CTA** — `pip install redactcli`

---

## Tweet 1 (main — attach MP4)

```
This is how AWS keys end up in Slack.

Your agent dumps a session log.
You paste it into chat.
Or commit debug.log.

One pipe:

cat agent.log | redactcli

CI can block the rest:

redactcli scan .

pip install redactcli
https://github.com/AshSgDe29071999/redactcli
```

---

## Tweet 2 (thread)

```
The scary part isn't "hackers."

It's normal workflow:

• Claude / Codex / Cursor session log
• "can someone check this error?"
• paste into #eng-help
• key is live for hours

redactcli is offline, pipe-first, and has a GitHub Action that fails the PR when secrets show up.
```

---

## Tweet 3 (thread)

```
Drop this in CLAUDE.md / AGENTS.md:

Before sharing logs or env dumps:
  cmd 2>&1 | redactcli

PyPI: https://pypi.org/project/redactcli/
Action: AshSgDe29071999/redactcli/action@v0.1.0
```

---

## LinkedIn

```
Shipping coding agents without redaction is how cloud keys land in Slack.

I built redactcli — a small offline CLI + GitHub Action that strips high-signal secrets from agent logs, diffs, and CI output.

pip install redactcli
cat dump.log | redactcli
redactcli scan .   # exit 1 if secrets found

No cloud. No API key. MIT.
https://github.com/AshSgDe29071999/redactcli
```

---

## Posting checklist

- [ ] Attach **MP4** (not a bare link)
- [ ] First line = pain, not product name
- [ ] Post Tue–Thu morning US
- [ ] Reply with thread 2 + 3 within 2 minutes
- [ ] Pin repo + put GIF near top of README
