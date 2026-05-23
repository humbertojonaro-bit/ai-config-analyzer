FROM python:3.12-slim AS build
WORKDIR /app
COPY pyproject.toml README.md LICENSE MANIFEST.in ./
COPY src ./src
RUN pip install --no-cache-dir --upgrade pip build \
    && pip install --no-cache-dir ".[api]"

FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin/ai-config-analyzer /usr/local/bin/ai-config-analyzer
COPY --from=build /usr/local/bin/uvicorn /usr/local/bin/uvicorn
RUN useradd --create-home --uid 10001 app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)" || exit 1
CMD ["uvicorn", "ai_config_analyzer.api:app", "--host", "0.0.0.0", "--port", "8000"]
