"""Built-in rule registry."""

from __future__ import annotations

from collections.abc import Callable

from ai_config_analyzer.findings import Finding
from ai_config_analyzer.rules.secrets import detect_secrets
from ai_config_analyzer.rules.security import detect_insecure_defaults
from ai_config_analyzer.rules.structure import detect_empty_values, detect_excessive_depth

Rule = Callable[[dict], list[Finding]]

BUILTIN_RULES: dict[str, Rule] = {
    "secrets": detect_secrets,
    "empty-values": detect_empty_values,
    "excessive-depth": detect_excessive_depth,
    "insecure-defaults": detect_insecure_defaults,
}

__all__ = ["BUILTIN_RULES", "Rule"]
