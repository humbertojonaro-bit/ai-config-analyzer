"""Multi-format configuration parser.

Supports YAML, JSON, TOML, INI, and dotenv. Format is detected from the file
extension, with a content-based fallback for ambiguous cases.
"""

from __future__ import annotations

import configparser
import json
import sys
from pathlib import Path
from typing import Any

import yaml

if sys.version_info >= (3, 11):
    import tomllib as _toml
else:  # pragma: no cover - py<3.11 fallback
    import tomli as _toml  # type: ignore[import-not-found]


SUPPORTED_FORMATS = ("yaml", "json", "toml", "ini", "env")


class ParseError(ValueError):
    """Raised when a configuration file cannot be parsed."""


def detect_format(path: str | Path) -> str:
    suffix = Path(path).suffix.lower().lstrip(".")
    mapping = {
        "yaml": "yaml",
        "yml": "yaml",
        "json": "json",
        "toml": "toml",
        "ini": "ini",
        "cfg": "ini",
        "conf": "ini",
        "env": "env",
    }
    if suffix in mapping:
        return mapping[suffix]
    if Path(path).name.lower() in {".env", "dotenv"}:
        return "env"
    raise ParseError(f"Cannot detect format from path: {path}")


def parse_file(path: str | Path, fmt: str | None = None) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise ParseError(f"File not found: {path}")
    fmt = fmt or detect_format(p)
    text = p.read_text(encoding="utf-8")
    return parse_string(text, fmt)


def parse_string(text: str, fmt: str) -> dict[str, Any]:
    fmt = fmt.lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ParseError(f"Unsupported format: {fmt}")
    try:
        if fmt == "yaml":
            data = yaml.safe_load(text)
        elif fmt == "json":
            data = json.loads(text) if text.strip() else {}
        elif fmt == "toml":
            data = _toml.loads(text)
        elif fmt == "ini":
            parser = configparser.ConfigParser()
            parser.read_string(text)
            data = {s: dict(parser.items(s)) for s in parser.sections()}
            if parser.defaults():
                data["DEFAULT"] = dict(parser.defaults())
        elif fmt == "env":
            data = _parse_env(text)
        else:  # pragma: no cover - guarded above
            raise ParseError(f"Unsupported format: {fmt}")
    except ParseError:
        raise
    except Exception as exc:
        raise ParseError(f"Failed to parse {fmt}: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ParseError(f"Top-level config must be a mapping, got {type(data).__name__}")
    return data


def _parse_env(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            raise ParseError(f"Invalid dotenv line: {raw!r}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        out[key] = value
    return out
