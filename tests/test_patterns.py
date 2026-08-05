"""Pattern unit tests — use clearly fake secrets only."""

from __future__ import annotations

from redactcli.engine import redact_text, scan_text
from redactcli.patterns import BUILTIN_PATTERNS, resolve_patterns


def test_builtin_patterns_named_uniquely():
    names = [p.name for p in BUILTIN_PATTERNS]
    assert len(names) == len(set(names))


def test_aws_access_key_redacted():
    # Classic fake AWS key shape (not a real credential).
    text = "export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
    result = redact_text(text)
    assert "AKIAIOSFODNN7EXAMPLE" not in result.text
    assert "AWS_ACCESS_KEY_ID" in result.text
    assert any(f.pattern == "aws_access_key_id" for f in result.findings)


def test_github_pat_redacted():
    text = "token=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ab"
    result = redact_text(text)
    assert "ghp_" not in result.text or "REDACTED" in result.text
    assert any(f.pattern == "github_pat" for f in result.findings)


def test_pem_block_redacted():
    text = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA0Z3VS5JJcds3xfn/fakeOnlyNotARealKey000000000000\n"
        "-----END RSA PRIVATE KEY-----\n"
    )
    result = redact_text(text)
    assert "BEGIN RSA PRIVATE KEY" not in result.text
    assert any(f.pattern == "pem_private_key" for f in result.findings)


def test_connection_string_redacted():
    text = "DATABASE_URL=postgres://user:s3cretPass@localhost:5432/app"
    result = redact_text(text)
    assert "s3cretPass" not in result.text
    assert any(f.pattern == "connection_string" for f in result.findings)


def test_pypi_token_redacted():
    text = "TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmcCJDEyMzQ1Njc4LWFiY2QtZWYwMTIzNDU2Nzg5"
    result = redact_text(text)
    assert "pypi-AgEI" not in result.text
    assert any(f.pattern == "pypi_token" for f in result.findings)


def test_scan_does_not_mutate():
    text = "key=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ab"
    findings = scan_text(text)
    assert findings
    assert "ghp_" in text


def test_min_confidence_high_filters_medium():
    # sk- keys are medium confidence (openai_api_key)
    text = "OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz012345"
    high_only = resolve_patterns(min_confidence="high")
    result_high = redact_text(text, patterns=high_only)
    # may or may not match other rules; openai should be excluded
    assert not any(f.pattern == "openai_api_key" for f in result_high.findings)

    medium = resolve_patterns(min_confidence="medium")
    result_med = redact_text(text, patterns=medium)
    assert any(f.pattern == "openai_api_key" for f in result_med.findings)


def test_clean_text_has_no_findings():
    text = "hello world from a unit test with no credentials"
    assert scan_text(text) == []
    result = redact_text(text)
    assert result.text == text
    assert result.findings == []
