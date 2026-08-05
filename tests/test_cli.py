"""CLI integration tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "redactcli", *args],
        cwd=str(ROOT),
        input=input_text,
        capture_output=True,
        text=True,
        env={**dict(**__import__("os").environ), "PYTHONPATH": str(ROOT / "src")},
    )


def test_redact_stdin():
    proc = _run(
        "redact",
        input_text="token ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ab\n",
    )
    assert proc.returncode == 0
    assert "ghp_" not in proc.stdout or "REDACTED" in proc.stdout
    assert "REDACTED" in proc.stdout


def test_scan_exits_one_on_secret():
    proc = _run(
        "scan",
        input_text="AKIAIOSFODNN7EXAMPLE\n",
    )
    assert proc.returncode == 1
    assert "aws_access_key_id" in proc.stdout


def test_scan_clean_exits_zero():
    proc = _run("scan", input_text="nothing sensitive here\n")
    assert proc.returncode == 0
    assert "No secrets found" in proc.stdout


def test_patterns_lists_builtins():
    proc = _run("patterns", "--json")
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    names = {row["name"] for row in data}
    assert "github_pat" in names
    assert "aws_access_key_id" in names


def test_default_subcommand_is_redact(tmp_path: Path):
    f = tmp_path / "a.txt"
    f.write_text("x=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ab\n", encoding="utf-8")
    proc = _run(str(f))
    assert proc.returncode == 0
    assert "REDACTED" in proc.stdout


def test_in_place(tmp_path: Path):
    f = tmp_path / "b.txt"
    f.write_text("AKIAIOSFODNN7EXAMPLE\n", encoding="utf-8")
    proc = _run("redact", "-i", str(f))
    assert proc.returncode == 0
    assert "AKIAIOSFODNN7EXAMPLE" not in f.read_text(encoding="utf-8")
