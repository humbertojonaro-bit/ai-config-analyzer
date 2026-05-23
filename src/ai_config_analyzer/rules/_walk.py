"""Shared traversal helpers."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any


def walk(data: Any, prefix: str = "") -> Iterator[tuple[str, Any]]:
    """Yield (dotted-path, value) for every leaf in a nested config."""
    if isinstance(data, dict):
        for k, v in data.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, (dict, list)):
                yield from walk(v, key)
            else:
                yield key, v
    elif isinstance(data, list):
        for i, v in enumerate(data):
            key = f"{prefix}[{i}]"
            if isinstance(v, (dict, list)):
                yield from walk(v, key)
            else:
                yield key, v
    else:
        yield prefix, data


def depth(data: Any) -> int:
    if isinstance(data, dict):
        return 1 + max((depth(v) for v in data.values()), default=0)
    if isinstance(data, list):
        return 1 + max((depth(v) for v in data), default=0)
    return 0
