# AI Config Analyzer

Analyze configuration files (YAML, JSON, TOML, INI, dotenv) for security issues,
insecure defaults, hard-coded secrets, and structural problems. Ships as a
Python library, a CLI, and an optional REST API.

## Install

```bash
pip install ai-config-analyzer            # library + CLI
pip install "ai-config-analyzer[api]"     # also install the REST API
```

For local development:

```bash
pip install -e ".[dev]"
pytest
```

## CLI quickstart

```bash
ai-config-analyzer analyze examples/insecure.yaml
ai-config-analyzer analyze examples/insecure.yaml --output json
ai-config-analyzer analyze examples/insecure.yaml --fail-on medium
ai-config-analyzer validate examples/insecure.yaml
```

Exit codes:
- `0` — no findings at/above `--fail-on` (default: `high`)
- `1` — findings at or above the threshold
- `2` — parse error

## Library

```python
from ai_config_analyzer import Analyzer

result = Analyzer().analyze_file("examples/insecure.yaml")
for f in result.findings:
    print(f.severity.value, f.rule_id, f.path, f.message)
```

## REST API

```bash
pip install "ai-config-analyzer[api]"
export AI_CONFIG_ANALYZER_API_KEYS="key-a,key-b"   # optional; omit to disable auth
uvicorn ai_config_analyzer.api:app --host 0.0.0.0 --port 8000
```

```bash
curl -X POST http://localhost:8000/analyze \
  -H "X-API-Key: key-a" \
  -H "Content-Type: application/json" \
  -d '{"content": "password: hunter2", "format": "yaml"}'
```

Endpoints:
- `GET /health` — liveness probe
- `POST /analyze` — analyze raw config text
- `GET /usage` — per-key request counts

## Docker

```bash
docker build -t ai-config-analyzer .
docker run --rm -p 8000:8000 -e AI_CONFIG_ANALYZER_API_KEYS=key-a ai-config-analyzer
```

## Built-in rules

| Rule ID | Severity | What it flags |
|---|---|---|
| `secrets.hardcoded` | high | Plaintext values for keys named `password`, `token`, `api_key`, etc. |
| `security.tls-verification-disabled` | high | `verify_ssl: false` and similar. |
| `security.debug-enabled` | medium | `debug: true`. |
| `security.bind-all-interfaces` | low | Services bound to `0.0.0.0` or `*`. |
| `structure.excessive-depth` | medium | Configuration nested more than 8 levels deep. |
| `structure.empty-value` | low | Keys with empty/`null` values. |

Disable a rule family via `--disable secrets` (CLI) or `"disable": ["secrets"]`
in the API request body.

## License

MIT — see [LICENSE](LICENSE).
