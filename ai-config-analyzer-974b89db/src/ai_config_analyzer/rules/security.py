"""Security-oriented rules: insecure defaults, debug flags, weak TLS, etc."""

from __future__ import annotations

from ai_config_analyzer.findings import Finding, Severity
from ai_config_analyzer.rules._walk import walk

INSECURE_HOSTS = {"0.0.0.0", "*"}
DEBUG_KEYS = {"debug", "debug_mode", "verbose_errors"}
TLS_DISABLE_KEYS = {"verify_ssl", "ssl_verify", "tls_verify", "verify"}


def detect_insecure_defaults(data: dict) -> list[Finding]:
    findings: list[Finding] = []
    for path, value in walk(data):
        last = path.rsplit(".", 1)[-1].rsplit("[", 1)[0].lower()

        if last in DEBUG_KEYS and _is_truthy(value):
            findings.append(
                Finding(
                    rule_id="security.debug-enabled",
                    message=f"Debug mode enabled at '{path}'",
                    severity=Severity.MEDIUM,
                    path=path,
                    remediation="Disable debug for production deployments.",
                )
            )

        if last in TLS_DISABLE_KEYS and _is_falsy(value):
            findings.append(
                Finding(
                    rule_id="security.tls-verification-disabled",
                    message=f"TLS verification disabled at '{path}'",
                    severity=Severity.HIGH,
                    path=path,
                    remediation="Enable TLS verification.",
                )
            )

        if last in {"host", "bind", "listen"} and isinstance(value, str) and value in INSECURE_HOSTS:
            findings.append(
                Finding(
                    rule_id="security.bind-all-interfaces",
                    message=f"Service binds to '{value}' at '{path}'",
                    severity=Severity.LOW,
                    path=path,
                    remediation="Bind to a specific interface or use a reverse proxy.",
                )
            )

    return findings


def _is_truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "on"}
    return False


def _is_falsy(value: object) -> bool:
    if isinstance(value, bool):
        return not value
    if isinstance(value, str):
        return value.strip().lower() in {"false", "0", "no", "off"}
    return False
