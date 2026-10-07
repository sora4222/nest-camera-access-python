"""Tests for saving and loading the Token."""

import json
import stat

import pytest

from googlenestcam.errors import TokenError
from googlenestcam.token_store import (
    default_token_path,
    load_refresh_token,
    save_refresh_token,
)


def test_default_path_is_in_user_config(tmp_path) -> None:
    """The Token lives in the user config folder, not the project."""
    assert default_token_path() == tmp_path / "config" / "googlenestcam" / "token.json"


def test_environment_overrides_path(monkeypatch, tmp_path) -> None:
    """GOOGLENESTCAM_TOKEN_PATH changes where the Token is kept."""
    monkeypatch.setenv("GOOGLENESTCAM_TOKEN_PATH", str(tmp_path / "t.json"))
    assert default_token_path() == tmp_path / "t.json"


def test_save_then_load(tmp_path) -> None:
    """A saved Token can be loaded again, and only the owner can read it."""
    path = tmp_path / "dir" / "token.json"
    save_refresh_token("refresh", path)
    assert load_refresh_token(path) == "refresh"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_save_uses_default_path() -> None:
    """Saving with no path uses the default path."""
    path = save_refresh_token("refresh")
    assert path == default_token_path()
    assert load_refresh_token() == "refresh"


def test_missing_token_returns_none(tmp_path) -> None:
    """No Token file means no Token."""
    assert load_refresh_token(tmp_path / "missing.json") is None


def test_environment_token_wins(monkeypatch, tmp_path) -> None:
    """A Token copied into GOOGLENESTCAM_REFRESH_TOKEN is used first."""
    path = tmp_path / "token.json"
    save_refresh_token("from-file", path)
    monkeypatch.setenv("GOOGLENESTCAM_REFRESH_TOKEN", "from-env")
    assert load_refresh_token(path) == "from-env"


def test_reads_existing_token_files(tmp_path) -> None:
    """Token files from the old video-stream app still load."""
    path = tmp_path / "token.json"
    path.write_text(json.dumps({"refresh_token": "old", "access_token": "x"}))
    assert load_refresh_token(path) == "old"


def test_broken_file_raises_clear_error(tmp_path) -> None:
    """A broken Token file gives an error with its path."""
    path = tmp_path / "token.json"
    path.write_text("not json")
    with pytest.raises(TokenError, match=str(path)):
        load_refresh_token(path)
