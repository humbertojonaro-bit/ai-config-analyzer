"""Top-level analyzer that runs registered rules over parsed config data."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai_config_analyzer.findings import Finding, Severity, severity_rank
from ai_config_analyzer.parser import parse_file, parse_string
from ai_config_analyzer.rules import BUILTIN_RULES, Rule


@dataclass
class AnalysisResult:
    findings: list[Finding] = field(default_factory=list)
    format: str = ""
    source: str = ""

    @property
    def highest_severity(self) -> Severity | None:
        if not self.findings:
            return None
        return max(self.findings, key=lambda f: severity_rank(f.severity)).severity

    def by_severity(self, severity: Severity) -> list[Finding]:
        return [f for f in self.findings if f.severity == severity]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "format": self.format,
            "highest_severity": self.highest_severity.value if self.highest_severity else None,
            "count": len(self.findings),
            "findings": [f.to_dict() for f in self.findings],
        }


class Analyzer:
    def __init__(
        self,
        rules: dict[str, Rule] | None = None,
        disabled: Iterable[str] = (),
    ) -> None:
        rules = dict(rules) if rules is not None else dict(BUILTIN_RULES)
        for name in disabled:
            rules.pop(name, None)
        self.rules = rules

    def analyze(self, data: dict, *, source: str = "", fmt: str = "") -> AnalysisResult:
        findings: list[Finding] = []
        for rule in self.rules.values():
            findings.extend(rule(data))
        findings.sort(key=lambda f: (-severity_rank(f.severity), f.rule_id, f.path))
        return AnalysisResult(findings=findings, format=fmt, source=source)

    def analyze_file(self, path: str | Path) -> AnalysisResult:
        from ai_config_analyzer.parser import detect_format

        fmt = detect_format(path)
        data = parse_file(path, fmt)
        return self.analyze(data, source=str(path), fmt=fmt)

    def analyze_string(self, text: str, fmt: str, *, source: str = "<inline>") -> AnalysisResult:
        data = parse_string(text, fmt)
        return self.analyze(data, source=source, fmt=fmt)
