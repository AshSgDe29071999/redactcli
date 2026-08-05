"""Built-in high-signal secret patterns and custom rule loading."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class Pattern:
    """A named secret detection rule."""

    name: str
    description: str
    regex: re.Pattern[str]
    replacement: str
    confidence: str = "high"  # high | medium

    def finditer(self, text: str) -> list[re.Match[str]]:
        return list(self.regex.finditer(text))


def _p(
    name: str,
    description: str,
    pattern: str,
    replacement: str,
    *,
    confidence: str = "high",
    flags: int = 0,
) -> Pattern:
    return Pattern(
        name=name,
        description=description,
        regex=re.compile(pattern, flags),
        replacement=replacement,
        confidence=confidence,
    )


# Order matters only for overlapping matches: more specific rules first.
BUILTIN_PATTERNS: tuple[Pattern, ...] = (
    _p(
        "pem_private_key",
        "PEM / OpenSSH private key block",
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----[\s\S]*?"
        r"-----END (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----",
        "[REDACTED:PEM_PRIVATE_KEY]",
    ),
    _p(
        "aws_access_key_id",
        "AWS access key id (AKIA/ASIA…)",
        r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",
        "[REDACTED:AWS_ACCESS_KEY_ID]",
    ),
    _p(
        "aws_secret_access_key",
        "AWS secret access key near assignment keywords",
        r"(?i)(?:aws_secret_access_key|aws_secret_key|secret_access_key)\s*[=:]\s*"
        r"['\"]?([A-Za-z0-9/+=]{40})['\"]?",
        r"\g<0>",  # replaced specially in engine for groups
        confidence="high",
    ),
    _p(
        "github_pat",
        "GitHub fine-grained or classic personal access token",
        r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,255}\b|"
        r"\bgithub_pat_[A-Za-z0-9_]{22,}_[A-Za-z0-9_]{59,}\b",
        "[REDACTED:GITHUB_TOKEN]",
    ),
    _p(
        "gitlab_pat",
        "GitLab personal access token",
        r"\bglpat-[A-Za-z0-9\-_]{20,}\b",
        "[REDACTED:GITLAB_TOKEN]",
    ),
    _p(
        "slack_token",
        "Slack bot/user token",
        r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b",
        "[REDACTED:SLACK_TOKEN]",
    ),
    _p(
        "stripe_key",
        "Stripe live/test secret key",
        r"\bsk_(?:live|test)_[A-Za-z0-9]{16,}\b",
        "[REDACTED:STRIPE_KEY]",
    ),
    _p(
        "openai_api_key",
        "OpenAI API key",
        r"\bsk-[A-Za-z0-9]{20,}\b",
        "[REDACTED:OPENAI_API_KEY]",
        confidence="medium",
    ),
    _p(
        "anthropic_api_key",
        "Anthropic API key",
        r"\bsk-ant-[A-Za-z0-9\-_]{20,}\b",
        "[REDACTED:ANTHROPIC_API_KEY]",
    ),
    _p(
        "pypi_token",
        "PyPI API token",
        r"\bpypi-[A-Za-z0-9_\-]{20,}\b",
        "[REDACTED:PYPI_TOKEN]",
    ),
    _p(
        "npm_token",
        "npm access token",
        r"\bnpm_[A-Za-z0-9]{36,}\b",
        "[REDACTED:NPM_TOKEN]",
    ),
    _p(
        "jwt",
        "JSON Web Token (three base64url segments)",
        r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b",
        "[REDACTED:JWT]",
        confidence="medium",
    ),
    _p(
        "connection_string",
        "Database URL with embedded credentials",
        r"(?i)\b(?:postgres|postgresql|mysql|mongodb(?:\+srv)?|redis|amqp|https?)://"
        r"[^\s/'\"<>]+:[^\s/'\"<>]+@[^\s'\"<>]+",
        "[REDACTED:CONNECTION_STRING]",
    ),
    _p(
        "generic_api_key_assignment",
        "Common secret assignment forms (api_key / token / password)",
        r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|"
        r"private[_-]?key|password|passwd|secret[_-]?key)\b\s*[=:]\s*"
        r"['\"]?([^\s'\"\\]{12,})['\"]?",
        r"\g<0>",
        confidence="medium",
    ),
    _p(
        "azure_storage_key",
        "Azure storage account key (base64-ish long secret near AccountKey)",
        r"(?i)(?:AccountKey|SharedAccessSignature)\s*=\s*([A-Za-z0-9+/=%]{20,})",
        r"\g<0>",
        confidence="medium",
    ),
    _p(
        "google_api_key",
        "Google API key",
        r"\bAIza[0-9A-Za-z\-_]{35}\b",
        "[REDACTED:GOOGLE_API_KEY]",
    ),
)


# Patterns that capture the secret in group 1 and need structured replacement.
_GROUP1_REPLACE: frozenset[str] = frozenset(
    {
        "aws_secret_access_key",
        "generic_api_key_assignment",
        "azure_storage_key",
    }
)


def is_group1_pattern(name: str) -> bool:
    return name in _GROUP1_REPLACE


def load_custom_patterns(path: Path) -> list[Pattern]:
    """Load extra patterns from JSON or YAML-ish JSON file.

    Expected shape::

        {
          "patterns": [
            {
              "name": "my_token",
              "description": "optional",
              "regex": "\\\\bfoo_[A-Za-z0-9]+\\\\b",
              "replacement": "[REDACTED:MY_TOKEN]",
              "confidence": "high"
            }
          ]
        }
    """
    raw = path.read_text(encoding="utf-8")
    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError:
        # Minimal YAML: only support JSON-compatible YAML via optional PyYAML — stay stdlib.
        # Accept a simple line-oriented fallback is not YAML; require JSON.
        raise ValueError(
            f"Custom rules file must be JSON: {path}. "
            "See README for the schema."
        ) from None

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict) and "patterns" in data:
        items = data["patterns"]
    else:
        raise ValueError("Custom rules must be a list or an object with a 'patterns' array")

    out: list[Pattern] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"patterns[{i}] must be an object")
        name = str(item.get("name") or f"custom_{i}")
        regex = item.get("regex")
        if not regex:
            raise ValueError(f"patterns[{i}] missing 'regex'")
        replacement = str(item.get("replacement") or f"[REDACTED:{name.upper()}]")
        description = str(item.get("description") or f"Custom pattern {name}")
        confidence = str(item.get("confidence") or "high")
        flags = re.IGNORECASE if item.get("ignore_case") else 0
        out.append(
            Pattern(
                name=name,
                description=description,
                regex=re.compile(str(regex), flags),
                replacement=replacement,
                confidence=confidence,
            )
        )
    return out


def resolve_patterns(
    *,
    include: set[str] | None = None,
    exclude: set[str] | None = None,
    custom: list[Pattern] | None = None,
    min_confidence: str = "medium",
) -> list[Pattern]:
    """Select active patterns."""
    rank = {"high": 2, "medium": 1, "low": 0}
    min_rank = rank.get(min_confidence, 1)
    selected: list[Pattern] = []
    for pat in BUILTIN_PATTERNS:
        if include is not None and pat.name not in include:
            continue
        if exclude is not None and pat.name in exclude:
            continue
        if rank.get(pat.confidence, 0) < min_rank:
            continue
        selected.append(pat)
    if custom:
        selected.extend(custom)
    return selected
