"""Tests for getting access tokens for Google's API."""

import httpx
import pytest

from googlenestcam import auth as auth_module
from googlenestcam.auth import GoogleAuth
from googlenestcam.credentials import Credentials
from googlenestcam.errors import MissingTokenError
from googlenestcam.token_store import save_refresh_token

CREDS = Credentials("id", "secret", "p")


def _client(responses: list[dict]) -> httpx.AsyncClient:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=responses.pop(0))

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_access_token_is_cached(tmp_path) -> None:
    """One refresh serves calls until the access token nears expiry."""
    path = tmp_path / "token.json"
    save_refresh_token("r", path)
    auth = GoogleAuth(CREDS, token_path=path)
    responses = [{"access_token": "a1", "expires_in": 3600}]
    async with _client(responses) as client:
        assert await auth.access_token(client) == "a1"
        assert await auth.access_token(client) == "a1"


async def test_expiring_access_token_is_refreshed(tmp_path) -> None:
    """An access token about to expire is replaced."""
    path = tmp_path / "token.json"
    save_refresh_token("r", path)
    auth = GoogleAuth(CREDS, token_path=path)
    responses = [
        {"access_token": "a1", "expires_in": 30},
        {"access_token": "a2", "expires_in": 3600},
    ]
    async with _client(responses) as client:
        assert await auth.access_token(client) == "a1"
        assert await auth.access_token(client) == "a2"


async def test_missing_token_can_raise(tmp_path) -> None:
    """With on_missing_token="raise", no Token means an error, not a browser."""
    auth = GoogleAuth(CREDS, token_path=tmp_path / "t.json", on_missing_token="raise")
    async with _client([]) as client:
        with pytest.raises(MissingTokenError, match="login"):
            await auth.access_token(client)


async def test_missing_token_runs_login_by_default(monkeypatch, tmp_path) -> None:
    """By default, no Token starts a Login first."""
    path = tmp_path / "t.json"

    def fake_login(**kwargs) -> None:
        save_refresh_token("r", kwargs["token_path"])

    monkeypatch.setattr(auth_module, "login", fake_login)
    auth = GoogleAuth(CREDS, token_path=path)
    async with _client([{"access_token": "a", "expires_in": 3600}]) as client:
        assert await auth.access_token(client) == "a"
