import pytest

from ai_config_analyzer.parser import (
    ParseError,
    detect_format,
    parse_file,
    parse_string,
)


def test_detect_format_known_extensions():
    assert detect_format("a.yaml") == "yaml"
    assert detect_format("a.yml") == "yaml"
    assert detect_format("a.json") == "json"
    assert detect_format("a.toml") == "toml"
    assert detect_format("a.ini") == "ini"
    assert detect_format("a.cfg") == "ini"
    assert detect_format("a.env") == "env"


def test_detect_format_unknown_raises():
    with pytest.raises(ParseError):
        detect_format("a.xyz")


def test_parse_yaml_basic():
    data = parse_string("a: 1\nb:\n  c: 2\n", "yaml")
    assert data == {"a": 1, "b": {"c": 2}}


def test_parse_json_empty_returns_empty_dict():
    assert parse_string("", "json") == {}


def test_parse_toml():
    data = parse_string('name = "x"\n[section]\nk = 1\n', "toml")
    assert data == {"name": "x", "section": {"k": 1}}


def test_parse_ini():
    text = "[server]\nhost = localhost\nport = 8080\n"
    data = parse_string(text, "ini")
    assert data == {"server": {"host": "localhost", "port": "8080"}}


def test_parse_env_handles_quotes_and_export():
    text = '\n'.join([
        "# comment",
        "FOO=bar",
        'BAZ="qux"',
        "export QUUX='zap'",
        "",
    ])
    assert parse_string(text, "env") == {"FOO": "bar", "BAZ": "qux", "QUUX": "zap"}


def test_parse_env_invalid_raises():
    with pytest.raises(ParseError):
        parse_string("not-a-pair", "env")


def test_parse_unsupported_format():
    with pytest.raises(ParseError):
        parse_string("x", "xml")


def test_parse_top_level_must_be_mapping():
    with pytest.raises(ParseError):
        parse_string("- 1\n- 2\n", "yaml")


def test_parse_file_roundtrip(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("a: 1\n", encoding="utf-8")
    assert parse_file(p) == {"a": 1}


def test_parse_file_missing(tmp_path):
    with pytest.raises(ParseError):
        parse_file(tmp_path / "nope.yaml")


def test_parse_invalid_yaml():
    with pytest.raises(ParseError):
        parse_string("a: [unbalanced", "yaml")
