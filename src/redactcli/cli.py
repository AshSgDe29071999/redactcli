"""Command-line interface for redactcli."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from redactcli import __version__
from redactcli.engine import Finding, redact_text, scan_text
from redactcli.patterns import (
    BUILTIN_PATTERNS,
    load_custom_patterns,
    resolve_patterns,
)


def _finding_row(finding: Finding, file_label: str) -> dict:
    row = asdict(finding)
    row["file"] = file_label
    return row


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="redactcli",
        description=(
            "Redact secrets from agent output, logs, diffs, and CI. "
            "Pipe-friendly: cat log | redactcli"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--rules",
        type=Path,
        metavar="FILE",
        help="JSON file with extra patterns",
    )
    common.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="NAME",
        help="Only use these built-in pattern names (repeatable)",
    )
    common.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="NAME",
        help="Skip these built-in pattern names (repeatable)",
    )
    common.add_argument(
        "--min-confidence",
        choices=("high", "medium"),
        default="medium",
        help="Minimum pattern confidence (default: medium)",
    )
    common.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit machine-readable JSON",
    )

    sub = parser.add_subparsers(dest="command")

    p_redact = sub.add_parser(
        "redact",
        parents=[common],
        help="Redact secrets from stdin and/or files (default command)",
    )
    p_redact.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Files to redact (default: stdin if none)",
    )
    p_redact.add_argument(
        "-i",
        "--in-place",
        action="store_true",
        help="Rewrite files in place (implies paths)",
    )
    p_redact.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write redacted output to this file instead of stdout",
    )

    p_scan = sub.add_parser(
        "scan",
        parents=[common],
        help="Report secrets without rewriting; exit 1 if any found",
    )
    p_scan.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Files to scan (default: stdin if none)",
    )
    p_scan.add_argument(
        "--fail-on-findings",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Exit 1 when secrets are found (default: true)",
    )

    p_patterns = sub.add_parser(
        "patterns",
        help="List built-in detection patterns",
    )
    p_patterns.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit JSON",
    )

    return parser


def _patterns_from_args(args: argparse.Namespace) -> list:
    custom = load_custom_patterns(args.rules) if getattr(args, "rules", None) else None
    include = set(args.include) if getattr(args, "include", None) else None
    exclude = set(args.exclude) if getattr(args, "exclude", None) else None
    if include is not None and not include:
        include = None
    if exclude is not None and not exclude:
        exclude = None
    return resolve_patterns(
        include=include,
        exclude=exclude,
        custom=custom,
        min_confidence=getattr(args, "min_confidence", "medium"),
    )


def _read_inputs(paths: list[Path]) -> list[tuple[str, str]]:
    if not paths:
        return [("<stdin>", sys.stdin.read())]
    out: list[tuple[str, str]] = []
    for path in paths:
        out.append((str(path), path.read_text(encoding="utf-8", errors="replace")))
    return out


def _cmd_patterns(args: argparse.Namespace) -> int:
    rows = [
        {
            "name": p.name,
            "confidence": p.confidence,
            "description": p.description,
        }
        for p in BUILTIN_PATTERNS
    ]
    if args.as_json:
        print(json.dumps(rows, indent=2))
    else:
        for row in rows:
            print(f"{row['name']:28} [{row['confidence']:6}]  {row['description']}")
    return 0


def _cmd_redact(args: argparse.Namespace) -> int:
    patterns = _patterns_from_args(args)
    inputs = _read_inputs(list(args.paths or []))
    combined_findings: list[dict] = []
    pieces: list[str] = []

    for label, text in inputs:
        result = redact_text(text, patterns=patterns)
        combined_findings.extend(_finding_row(f, label) for f in result.findings)
        if args.in_place and label != "<stdin>":
            Path(label).write_text(result.text, encoding="utf-8")
        pieces.append(result.text)

    output_text = pieces[0] if len(pieces) == 1 else "\n".join(pieces)

    if args.as_json:
        print(
            json.dumps(
                {
                    "count": len(combined_findings),
                    "findings": combined_findings,
                    "text": output_text,
                },
                indent=2,
            )
        )
        return 0

    if args.output:
        args.output.write_text(output_text, encoding="utf-8")
    elif not args.in_place:
        sys.stdout.write(output_text)
        if output_text and not output_text.endswith("\n"):
            sys.stdout.write("\n")

    if combined_findings:
        print(
            f"# redactcli: redacted {len(combined_findings)} finding(s)",
            file=sys.stderr,
        )
    return 0


def _cmd_scan(args: argparse.Namespace) -> int:
    patterns = _patterns_from_args(args)
    inputs = _read_inputs(list(args.paths or []))
    all_findings: list[dict] = []
    for label, text in inputs:
        findings = scan_text(text, patterns=patterns)
        for f in findings:
            all_findings.append(_finding_row(f, label))

    if args.as_json:
        print(json.dumps({"count": len(all_findings), "findings": all_findings}, indent=2))
    else:
        if not all_findings:
            print("No secrets found.")
        else:
            for f in all_findings:
                print(
                    f"{f['file']}:{f['line']}:{f['column']}: "
                    f"{f['pattern']} ({f['confidence']})  {f['excerpt']}"
                )
            print(f"\n{len(all_findings)} finding(s)", file=sys.stderr)

    if all_findings and args.fail_on_findings:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    raw = list(sys.argv[1:] if argv is None else argv)

    commands = {"redact", "scan", "patterns"}
    if not raw:
        raw = ["redact"]
    elif raw[0] not in commands and raw[0] not in {"-h", "--help", "--version"}:
        raw = ["redact", *raw]

    args = parser.parse_args(raw)
    if args.command is None:
        args = parser.parse_args(["redact"])

    try:
        if args.command == "patterns":
            return _cmd_patterns(args)
        if args.command == "scan":
            return _cmd_scan(args)
        if args.command == "redact":
            return _cmd_redact(args)
        parser.error(f"unknown command: {args.command}")
        return 2
    except (OSError, ValueError) as exc:
        print(f"redactcli: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
