import pytest


@pytest.fixture
def sample_yaml() -> str:
    return (
        "service:\n"
        "  name: payments\n"
        "  host: 0.0.0.0\n"
        "  debug: true\n"
        "database:\n"
        "  password: hunter2\n"
        "  verify_ssl: false\n"
        "feature_flags:\n"
        "  new_ui: ${NEW_UI}\n"
        "empty_key: \"\"\n"
    )


@pytest.fixture
def clean_yaml() -> str:
    return (
        "service:\n"
        "  name: payments\n"
        "  host: 127.0.0.1\n"
        "  debug: false\n"
        "database:\n"
        "  password: ${DB_PASSWORD}\n"
        "  verify_ssl: true\n"
    )
