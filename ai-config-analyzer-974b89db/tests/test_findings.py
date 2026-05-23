from ai_config_analyzer.findings import Finding, Severity, severity_rank


def test_severity_rank_ordering():
    assert severity_rank(Severity.CRITICAL) > severity_rank(Severity.HIGH)
    assert severity_rank(Severity.HIGH) > severity_rank(Severity.MEDIUM)
    assert severity_rank(Severity.MEDIUM) > severity_rank(Severity.LOW)
    assert severity_rank(Severity.LOW) > severity_rank(Severity.INFO)


def test_finding_to_dict_serializes_severity():
    f = Finding(rule_id="r", message="m", severity=Severity.HIGH, path="a.b")
    d = f.to_dict()
    assert d["severity"] == "high"
    assert d["rule_id"] == "r"
    assert d["path"] == "a.b"


def test_severity_rank_accepts_string():
    assert severity_rank("high") == severity_rank(Severity.HIGH)
