"""Detect hard-coded secrets in configuration values."""

from __future__ import annotations

import re

from ai_config_analyzer.findings import Finding, Severity
from ai_config_analyzer.rules._walk import walk

SECRET_KEY_PATTERN = re.compile(
    r"(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key)",
    re.IGNORECASE,
)
PLACEHOLDER_PATTERN = re.compile(r"^(\$\{.+\}|<.+>|changeme|todo|xxx+)$", re.IGNORECASE)


def detect_secrets(data: dict) -> list[Finding]:
    findings: list[Finding] = []
    for path, value in walk(data):
        if not isinstance(value, str) or not value:
            continue
        last = path.rsplit(".", 1)[-1].rsplit("[", 1)[0]
        if not SECRET_KEY_PATTERN.search(last):
            continue
        if PLACEHOLDER_PATTERN.match(value.strip()):
            continue
        findings.append(
            Finding(
                rule_id="secrets.hardcoded",
                message=f"Possible hard-coded secret at '{path}'",
                severity=Severity.HIGH,
                path=path,
                remediation="Move the secret to an environment variable or secret manager.",
            )
        )
    return findings
