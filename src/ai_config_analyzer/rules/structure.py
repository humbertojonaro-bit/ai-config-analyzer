"""Structural rules."""

from __future__ import annotations

from ai_config_analyzer.findings import Finding, Severity
from ai_config_analyzer.rules._walk import depth, walk

MAX_DEPTH = 8


def detect_empty_values(data: dict) -> list[Finding]:
    findings: list[Finding] = []
    for path, value in walk(data):
        if value is None or (isinstance(value, str) and value.strip() == ""):
            findings.append(
                Finding(
                    rule_id="structure.empty-value",
                    message=f"Empty value at '{path}'",
                    severity=Severity.LOW,
                    path=path,
                    remediation="Remove the key or provide a value.",
                )
            )
    return findings


def detect_excessive_depth(data: dict) -> list[Finding]:
    d = depth(data)
    if d > MAX_DEPTH:
        return [
            Finding(
                rule_id="structure.excessive-depth",
                message=f"Configuration nesting depth {d} exceeds recommended {MAX_DEPTH}",
                severity=Severity.MEDIUM,
                path="",
                remediation="Flatten the configuration to improve readability.",
                metadata={"depth": d, "max": MAX_DEPTH},
            )
        ]
    return []
