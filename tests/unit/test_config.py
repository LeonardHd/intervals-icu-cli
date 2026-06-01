import pytest

from intervals_icu_cli import config as config_module
from intervals_icu_cli.client import IntervalsAuthError, IntervalsConfig


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Point config at a temp dir and clear credential env vars."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    for var in (
        "INTERVALS_ICU_ATHLETE_ID",
        "INTERVALS_ICU_API_KEY",
        "INTERVALS_ICU_BASE_URL",
    ):
        monkeypatch.delenv(var, raising=False)
    return tmp_path


def test_write_and_read_roundtrip():
    path = config_module.write_config_file(athlete_id="i123", api_key="secret")

    assert path == config_module.config_path()
    assert (path.stat().st_mode & 0o777) == 0o600

    data = config_module.read_config_file()
    assert data["athlete_id"] == "i123"
    assert data["api_key"] == "secret"


def test_read_missing_returns_empty():
    assert config_module.read_config_file() == {}


def test_delete_config_file():
    config_module.write_config_file(athlete_id="i123", api_key="secret")
    assert config_module.delete_config_file() is True
    assert config_module.delete_config_file() is False


def test_resolve_uses_file_when_no_env():
    config_module.write_config_file(athlete_id="i123", api_key="secret")

    resolved = IntervalsConfig.resolve()

    assert resolved.athlete_id == "i123"
    assert resolved.api_key == "secret"
    assert resolved.base_url == "https://intervals.icu"


def test_resolve_prefers_env_over_file(monkeypatch):
    config_module.write_config_file(athlete_id="file-id", api_key="file-key")
    monkeypatch.setenv("INTERVALS_ICU_ATHLETE_ID", "env-id")
    monkeypatch.setenv("INTERVALS_ICU_API_KEY", "env-key")

    resolved = IntervalsConfig.resolve()

    assert resolved.athlete_id == "env-id"
    assert resolved.api_key == "env-key"


def test_resolve_strips_trailing_slash_from_base_url():
    config_module.write_config_file(
        athlete_id="i123", api_key="secret", base_url="https://example.com/"
    )

    assert IntervalsConfig.resolve().base_url == "https://example.com"


def test_resolve_raises_when_missing():
    with pytest.raises(IntervalsAuthError):
        IntervalsConfig.resolve()
