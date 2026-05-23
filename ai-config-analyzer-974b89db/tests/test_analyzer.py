from ai_config_analyzer.analyzer import Analyzer
from ai_config_analyzer.findings import Severity
from ai_config_analyzer.parser import parse_string


def _rule_ids(result):
    return {f.rule_id for f in result.findings}


def test_clean_config_has_no_high_severity(clean_yaml):
    analyzer = Analyzer()
    data = parse_string(clean_yaml, "yaml")
    result = analyzer.analyze(data, fmt="yaml")
    assert all(f.severity != Severity.HIGH for f in result.findings)


def test_detects_secret(sample_yaml):
    analyzer = Analyzer()
    data = parse_string(sample_yaml, "yaml")
    result = analyzer.analyze(data, fmt="yaml")
    assert "secrets.hardcoded" in _rule_ids(result)
    secret_findings = [f for f in result.findings if f.rule_id == "secrets.hardcoded"]
    assert any("database.password" in f.path for f in secret_findings)


def test_placeholder_secret_ignored():
    analyzer = Analyzer()
    data = parse_string("password: ${DB_PASSWORD}\n", "yaml")
    result = analyzer.analyze(data, fmt="yaml")
    assert "secrets.hardcoded" not in _rule_ids(result)


def test_detects_debug_and_tls_and_bind(sample_yaml):
    analyzer = Analyzer()
    data = parse_string(sample_yaml, "yaml")
    result = analyzer.analyze(data, fmt="yaml")
    ids = _rule_ids(result)
    assert "security.debug-enabled" in ids
    assert "security.tls-verification-disabled" in ids
    assert "security.bind-all-interfaces" in ids


def test_detects_empty_value(sample_yaml):
    analyzer = Analyzer()
    data = parse_string(sample_yaml, "yaml")
    result = analyzer.analyze(data, fmt="yaml")
    assert "structure.empty-value" in _rule_ids(result)


def test_excessive_depth():
    nested = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": 1}}}}}}}}}
    result = Analyzer().analyze(nested)
    assert "structure.excessive-depth" in _rule_ids(result)


def test_disabled_rule_not_run(sample_yaml):
    analyzer = Analyzer(disabled=["secrets"])
    data = parse_string(sample_yaml, "yaml")
    result = analyzer.analyze(data, fmt="yaml")
    assert "secrets.hardcoded" not in _rule_ids(result)


def test_highest_severity_and_to_dict(sample_yaml):
    analyzer = Analyzer()
    data = parse_string(sample_yaml, "yaml")
    result = analyzer.analyze(data, fmt="yaml", source="x.yaml")
    assert result.highest_severity == Severity.HIGH
    d = result.to_dict()
    assert d["source"] == "x.yaml"
    assert d["format"] == "yaml"
    assert d["count"] == len(result.findings)
    assert isinstance(d["findings"], list)


def test_findings_sorted_by_severity_desc(sample_yaml):
    data = parse_string(sample_yaml, "yaml")
    result = Analyzer().analyze(data, fmt="yaml")
    from ai_config_analyzer.findings import severity_rank

    ranks = [severity_rank(f.severity) for f in result.findings]
    assert ranks == sorted(ranks, reverse=True)
