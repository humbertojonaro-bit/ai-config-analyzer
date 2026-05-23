import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from ai_config_analyzer.api import create_app


@pytest.fixture
def client_no_auth():
    return TestClient(create_app(api_keys=set()))


@pytest.fixture
def client_with_auth():
    return TestClient(create_app(api_keys={"test-key"}))


def test_health(client_no_auth):
    r = client_no_auth.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze_no_auth(client_no_auth, sample_yaml):
    r = client_no_auth.post("/analyze", json={"content": sample_yaml, "format": "yaml"})
    assert r.status_code == 200
    body = r.json()
    assert body["count"] >= 1
    assert any(f["rule_id"] == "secrets.hardcoded" for f in body["findings"])


def test_analyze_requires_key(client_with_auth, sample_yaml):
    r = client_with_auth.post("/analyze", json={"content": sample_yaml, "format": "yaml"})
    assert r.status_code == 401


def test_analyze_with_key(client_with_auth, sample_yaml):
    r = client_with_auth.post(
        "/analyze",
        json={"content": sample_yaml, "format": "yaml"},
        headers={"X-API-Key": "test-key"},
    )
    assert r.status_code == 200


def test_analyze_bad_format(client_no_auth):
    r = client_no_auth.post("/analyze", json={"content": "x", "format": "xml"})
    assert r.status_code == 400


def test_analyze_parse_error(client_no_auth):
    r = client_no_auth.post(
        "/analyze", json={"content": "a: [unterminated", "format": "yaml"}
    )
    assert r.status_code == 400


def test_usage_meters_requests(client_with_auth, sample_yaml):
    headers = {"X-API-Key": "test-key"}
    for _ in range(3):
        client_with_auth.post(
            "/analyze", json={"content": sample_yaml, "format": "yaml"}, headers=headers
        )
    r = client_with_auth.get("/usage", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 3
    assert data["counts"]["test-key"] >= 3


def test_disable_rule_via_api(client_no_auth, sample_yaml):
    r = client_no_auth.post(
        "/analyze",
        json={"content": sample_yaml, "format": "yaml", "disable": ["secrets"]},
    )
    assert r.status_code == 200
    ids = {f["rule_id"] for f in r.json()["findings"]}
    assert "secrets.hardcoded" not in ids
