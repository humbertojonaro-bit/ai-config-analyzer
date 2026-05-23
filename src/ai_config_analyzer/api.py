"""FastAPI service exposing the analyzer over HTTP.

The API requires an API key via the ``X-API-Key`` header. Keys are read from the
``AI_CONFIG_ANALYZER_API_KEYS`` environment variable (comma-separated). A simple
in-memory metering counter tracks request counts per key and is exposed at
``/usage``.
"""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from ai_config_analyzer import __version__
from ai_config_analyzer.analyzer import Analyzer
from ai_config_analyzer.parser import SUPPORTED_FORMATS, ParseError


class AnalyzeRequest(BaseModel):
    content: str = Field(..., description="Raw configuration text.")
    format: str = Field(..., description=f"One of: {', '.join(SUPPORTED_FORMATS)}")
    disable: list[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    source: str
    format: str
    highest_severity: str | None
    count: int
    findings: list[dict[str, Any]]


def _load_keys() -> set[str]:
    raw = os.environ.get("AI_CONFIG_ANALYZER_API_KEYS", "").strip()
    if not raw:
        return set()
    return {k.strip() for k in raw.split(",") if k.strip()}


class Meter:
    """Thread-safe in-process request counter."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counts: dict[str, int] = defaultdict(int)
        self._started = time.time()

    def record(self, key: str) -> int:
        with self._lock:
            self._counts[key] += 1
            return self._counts[key]

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "started_at": self._started,
                "uptime_seconds": time.time() - self._started,
                "counts": dict(self._counts),
                "total": sum(self._counts.values()),
            }


def create_app(api_keys: set[str] | None = None, meter: Meter | None = None) -> FastAPI:
    app = FastAPI(
        title="AI Config Analyzer",
        version=__version__,
        description="Analyze configuration files for security and structural issues.",
    )
    keys = set(api_keys) if api_keys is not None else _load_keys()
    metering = meter or Meter()

    def require_key(x_api_key: str | None = Header(default=None)) -> str:
        if not keys:
            return "anonymous"
        if x_api_key is None or x_api_key not in keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid API key.",
            )
        metering.record(x_api_key)
        return x_api_key

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/usage")
    def usage(key: str = Depends(require_key)) -> dict[str, Any]:
        return metering.snapshot()

    @app.post("/analyze", response_model=AnalyzeResponse)
    def analyze(req: AnalyzeRequest, key: str = Depends(require_key)) -> AnalyzeResponse:
        if req.format not in SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {req.format}",
            )
        analyzer = Analyzer(disabled=req.disable)
        try:
            result = analyzer.analyze_string(req.content, req.format, source="<api>")
        except ParseError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc
        return AnalyzeResponse(**result.to_dict())

    return app


app = create_app()
