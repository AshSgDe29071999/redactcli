"""Custom rules file loading."""

from __future__ import annotations

import json
from pathlib import Path

from redactcli.engine import redact_text
from redactcli.patterns import load_custom_patterns, resolve_patterns


def test_custom_rule_json(tmp_path: Path):
    rules = tmp_path / "rules.json"
    rules.write_text(
        json.dumps(
            {
                "patterns": [
                    {
                        "name": "demo_token",
                        "regex": r"\bDEMO_[A-Z0-9]{8}\b",
                        "replacement": "[REDACTED:DEMO]",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    custom = load_custom_patterns(rules)
    patterns = resolve_patterns(custom=custom, min_confidence="high")
    result = redact_text("prefix DEMO_ABCD1234 suffix", patterns=patterns)
    assert "DEMO_ABCD1234" not in result.text
    assert "[REDACTED:DEMO]" in result.text
