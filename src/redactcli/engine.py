"""Core redaction / scan engine."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

from redactcli.patterns import Pattern, is_group1_pattern, resolve_patterns


@dataclass(frozen=True, slots=True)
class Finding:
    """One secret match in the input text."""

    pattern: str
    description: str
    confidence: str
    line: int
    column: int
    excerpt: str
    start: int
    end: int


@dataclass(slots=True)
class RedactResult:
    """Outcome of redacting or scanning text."""

    text: str
    findings: list[Finding] = field(default_factory=list)
    redacted: bool = False

    @property
    def count(self) -> int:
        return len(self.findings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "redacted": self.redacted,
            "findings": [asdict(f) for f in self.findings],
            "text": self.text if self.redacted else None,
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


def _line_col(text: str, index: int) -> tuple[int, int]:
    line = text.count("\n", 0, index) + 1
    last_nl = text.rfind("\n", 0, index)
    col = index - last_nl
    return line, col


def _excerpt(text: str, start: int, end: int, *, width: int = 48) -> str:
    left = max(0, start - 12)
    right = min(len(text), end + 12)
    chunk = text[left:right].replace("\n", "\\n")
    if len(chunk) > width:
        chunk = chunk[: width - 1] + "…"
    return chunk


def _replacement_for(pattern: Pattern, match: Any) -> str:
    if is_group1_pattern(pattern.name) and match.lastindex:
        full = match.group(0)
        secret = match.group(1)
        # Preserve key= structure, redact only the secret value.
        return full.replace(secret, f"[REDACTED:{pattern.name.upper()}]", 1)
    if pattern.replacement.startswith(r"\g"):
        return f"[REDACTED:{pattern.name.upper()}]"
    return pattern.replacement


def scan_text(
    text: str,
    *,
    patterns: list[Pattern] | None = None,
) -> list[Finding]:
    """Return all findings without mutating text."""
    active = patterns if patterns is not None else resolve_patterns()
    findings: list[Finding] = []
    for pat in active:
        for m in pat.finditer(text):
            start, end = m.start(), m.end()
            line, col = _line_col(text, start)
            findings.append(
                Finding(
                    pattern=pat.name,
                    description=pat.description,
                    confidence=pat.confidence,
                    line=line,
                    column=col,
                    excerpt=_excerpt(text, start, end),
                    start=start,
                    end=end,
                )
            )
    findings.sort(key=lambda f: (f.start, f.end))
    return findings


def redact_text(
    text: str,
    *,
    patterns: list[Pattern] | None = None,
) -> RedactResult:
    """Redact all matching secrets; return cleaned text + findings."""
    active = patterns if patterns is not None else resolve_patterns()
    # Collect all matches with pattern, then apply right-to-left.
    spans: list[tuple[int, int, Pattern, Any]] = []
    for pat in active:
        for m in pat.finditer(text):
            spans.append((m.start(), m.end(), pat, m))

    # Drop nested/overlapping spans: keep earliest, longest-first on ties.
    spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
    kept: list[tuple[int, int, Pattern, Any]] = []
    occupied_until = -1
    for start, end, pat, m in spans:
        if start < occupied_until:
            continue
        kept.append((start, end, pat, m))
        occupied_until = end

    findings: list[Finding] = []
    for start, end, pat, _m in kept:
        line, col = _line_col(text, start)
        findings.append(
            Finding(
                pattern=pat.name,
                description=pat.description,
                confidence=pat.confidence,
                line=line,
                column=col,
                excerpt=_excerpt(text, start, end),
                start=start,
                end=end,
            )
        )

    # Apply replacements from the end so indices stay valid.
    out = text
    for start, end, pat, m in sorted(kept, key=lambda s: s[0], reverse=True):
        rep = _replacement_for(pat, m)
        out = out[:start] + rep + out[end:]

    findings.sort(key=lambda f: (f.start, f.end))
    return RedactResult(text=out, findings=findings, redacted=True)
