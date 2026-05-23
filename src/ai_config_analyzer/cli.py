"""Command-line interface for ai-config-analyzer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from ai_config_analyzer import __version__
from ai_config_analyzer.analyzer import Analyzer
from ai_config_analyzer.findings import Severity, severity_rank
from ai_config_analyzer.parser import SUPPORTED_FORMATS, ParseError

SEVERITY_CHOICES = [s.value for s in Severity]


@click.group()
@click.version_option(__version__, prog_name="ai-config-analyzer")
def main() -> None:
    """Analyze configuration files for security and structural issues."""


@main.command()
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--format",
    "fmt",
    type=click.Choice(list(SUPPORTED_FORMATS)),
    default=None,
    help="Force input format (auto-detected from extension by default).",
)
@click.option(
    "--output",
    "output_fmt",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format.",
)
@click.option(
    "--fail-on",
    type=click.Choice(SEVERITY_CHOICES),
    default="high",
    show_default=True,
    help="Exit with code 1 if any finding meets or exceeds this severity.",
)
@click.option("--disable", multiple=True, help="Rule name to disable (repeatable).")
def analyze(
    path: Path,
    fmt: str | None,
    output_fmt: str,
    fail_on: str,
    disable: tuple[str, ...],
) -> None:
    """Analyze a configuration file."""
    analyzer = Analyzer(disabled=disable)
    try:
        if fmt:
            result = analyzer.analyze_string(path.read_text(encoding="utf-8"), fmt, source=str(path))
        else:
            result = analyzer.analyze_file(path)
    except ParseError as exc:
        click.echo(f"error: {exc}", err=True)
        sys.exit(2)

    if output_fmt == "json":
        click.echo(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        _render_table(result)

    threshold = severity_rank(Severity(fail_on))
    if any(severity_rank(f.severity) >= threshold for f in result.findings):
        sys.exit(1)


@main.command()
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--format",
    "fmt",
    type=click.Choice(list(SUPPORTED_FORMATS)),
    default=None,
)
def validate(path: Path, fmt: str | None) -> None:
    """Validate that a file is parseable."""
    from ai_config_analyzer.parser import parse_file

    try:
        parse_file(path, fmt)
    except ParseError as exc:
        click.echo(f"invalid: {exc}", err=True)
        sys.exit(1)
    click.echo(f"ok: {path}")


def _render_table(result) -> None:
    if not result.findings:
        click.echo(f"No findings for {result.source}")
        return
    click.echo(f"Findings for {result.source} ({result.format}):")
    width = max(len(f.rule_id) for f in result.findings)
    for f in result.findings:
        click.echo(f"  [{f.severity.value:<8}] {f.rule_id:<{width}}  {f.path}  {f.message}")
    click.echo(f"Total: {len(result.findings)}  (highest: {result.highest_severity.value})")


if __name__ == "__main__":  # pragma: no cover
    main()
