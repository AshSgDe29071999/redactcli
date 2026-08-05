"""redactcli — redact secrets from agent output, logs, diffs, and CI."""

from __future__ import annotations

from redactcli.engine import Finding, RedactResult, redact_text, scan_text
from redactcli.patterns import BUILTIN_PATTERNS, Pattern

__version__ = "0.1.0"
__all__ = [
    "BUILTIN_PATTERNS",
    "Finding",
    "Pattern",
    "RedactResult",
    "redact_text",
    "scan_text",
    "__version__",
]
