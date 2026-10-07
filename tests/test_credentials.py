"""Tests for loading Credentials."""

import pytest

from googlenestcam import settings
from googlenestcam.credentials import Credentials, load_credentials
from googlenestcam.errors import CredentialsError, OnePasswordError


def test_arguments_are_used() -> None:
    """Values passed in code are used as given."""
    creds = load_credentials(client_id="id", client_secret="secret", project_id="p")
    assert creds == Credentials("id", "secret", "p")


def test_arguments_win_over_environment(monkeypatch) -> None:
    """Values passed in code win over environment variables."""
    monkeypatch.setenv("GOOGLENESTCAM_CLIENT_ID", "env-id")
    monkeypatch.setenv("GOOGLENESTCAM_CLIENT_SECRET", "env-secret")
    monkeypatch.setenv("GOOGLENESTCAM_PROJECT_ID", "env-p")
    creds = load_credentials(client_id="id")
    assert creds == Credentials("id", "env-secret", "env-p")


def test_one_password_references_are_resolved(monkeypatch) -> None:
    """Environment values starting with op:// are read from 1Password."""
    monkeypatch.setenv("GOOGLENESTCAM_CLIENT_ID", "op://vault/item/id")
    monkeypatch.setattr(settings, "resolve_reference", lambda ref: f"resolved {ref}")
    creds = load_credentials(client_secret="secret", project_id="p")
    assert creds.client_id == "resolved op://vault/item/id"


def test_one_password_failure_gives_clear_error(monkeypatch) -> None:
    """A failing 1Password lookup warns and ends in a clear error, not a crash."""

    def fail(_: str) -> str:
        raise OnePasswordError("1Password is down")

    monkeypatch.setenv("GOOGLENESTCAM_CLIENT_ID", "op://vault/item/id")
    monkeypatch.setattr(settings, "resolve_reference", fail)
    with pytest.warns(UserWarning, match="1Password is down"):
        with pytest.raises(CredentialsError, match="GOOGLENESTCAM_CLIENT_ID"):
            load_credentials(client_secret="secret", project_id="p")


def test_missing_values_are_all_named() -> None:
    """The error names every missing value and how to set it."""
    with pytest.raises(CredentialsError) as error:
        load_credentials(client_id="id")
    assert "client_secret" in str(error.value)
    assert "GOOGLENESTCAM_PROJECT_ID" in str(error.value)


def test_repr_hides_the_secret() -> None:
    """The client secret never appears in printed Credentials."""
    assert "hunter2" not in repr(Credentials("id", "hunter2", "p"))
