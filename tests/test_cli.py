import json

from click.testing import CliRunner

from ai_config_analyzer.cli import main


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "ai-config-analyzer" in result.output


def test_cli_analyze_table_clean(tmp_path, clean_yaml):
    p = tmp_path / "c.yaml"
    p.write_text(clean_yaml, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", str(p), "--fail-on", "high"])
    assert result.exit_code == 0
    assert "No findings" in result.output or "Findings" in result.output


def test_cli_analyze_json_and_fail_on(tmp_path, sample_yaml):
    p = tmp_path / "c.yaml"
    p.write_text(sample_yaml, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", str(p), "--output", "json", "--fail-on", "high"])
    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["count"] >= 1
    assert payload["highest_severity"] in {"high", "critical"}


def test_cli_validate_ok(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("a: 1\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["validate", str(p)])
    assert result.exit_code == 0
    assert "ok" in result.output


def test_cli_validate_bad(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("a: [unterminated", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["validate", str(p)])
    assert result.exit_code == 1


def test_cli_analyze_disable_rule(tmp_path, sample_yaml):
    p = tmp_path / "c.yaml"
    p.write_text(sample_yaml, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["analyze", str(p), "--output", "json", "--disable", "secrets", "--fail-on", "critical"],
    )
    payload = json.loads(result.output)
    rule_ids = {f["rule_id"] for f in payload["findings"]}
    assert "secrets.hardcoded" not in rule_ids
