"""Tests for signing API requests with a fresh access token."""

import httpx
import pytest

from googlenestcam import auth as auth_module
from googlenestcam.auth import GoogleAuth
from googlenestcam.credentials import Credentials
from googlenestcam.errors import MissingTokenError
from googlenestcam.token_store import save_refresh_token

CREDS = Credentials("id", "secret", "p")
API = "https://smartdevicemanagement.googleapis.com/v1/x"


def _client(auth: GoogleAuth, tokens: list[dict], seen: list) -> httpx.AsyncClient:
    """A client whose fake Google hands out ``tokens`` and logs API calls."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "oauth2.googleapis.com":
            return httpx.Response(200, json=tokens.pop(0))
        seen.append(request.headers["Authorization"])
        return httpx.Response(200, json={})

    return httpx.AsyncClient(auth=auth, transport=httpx.MockTransport(handler))


async def test_access_token_is_cached(tmp_path) -> None:
    """One refresh signs requests until the access token nears expiry."""
    path = tmp_path / "token.json"
    save_refresh_token("r", path)
    tokens = [{"access_token": "a1", "expires_in": 3600}]
    seen: list[str] = []
    async with _client(GoogleAuth(CREDS, token_path=path), tokens, seen) as client:
        await client.get(API)
        await client.get(API)
    assert seen == ["Bearer a1", "Bearer a1"]


async def test_expiring_access_token_is_refreshed(tmp_path) -> None:
    """An access token about to expire is replaced."""
    path = tmp_path / "token.json"
    save_refresh_token("r", path)
    tokens = [
        {"access_token": "a1", "expires_in": 30},
        {"access_token": "a2", "expires_in": 3600},
    ]
    seen: list[str] = []
    async with _client(GoogleAuth(CREDS, token_path=path), tokens, seen) as client:
        await client.get(API)
        await client.get(API)
    assert seen == ["Bearer a1", "Bearer a2"]


async def test_missing_token_can_raise(tmp_path) -> None:
    """With on_missing_token="raise", no Token means an error, not a browser."""
    auth = GoogleAuth(CREDS, token_path=tmp_path / "t.json", on_missing_token="raise")
    async with _client(auth, [], []) as client:
        with pytest.raises(MissingTokenError, match="login"):
            await client.get(API)


async def test_missing_token_runs_login_by_default(monkeypatch, tmp_path) -> None:
    """By default, no Token starts a Login first."""
    path = tmp_path / "t.json"

    def fake_login(**kwargs) -> None:
        save_refresh_token("r", kwargs["token_path"])

    monkeypatch.setattr(auth_module, "login", fake_login)
    tokens = [{"access_token": "a", "expires_in": 3600}]
    seen: list[str] = []
    async with _client(GoogleAuth(CREDS, token_path=path), tokens, seen) as client:
        await client.get(API)
    assert seen == ["Bearer a"]


def test_sync_client_is_refused(tmp_path) -> None:
    """GoogleAuth refreshes on the background loop, so only AsyncClient works."""
    auth = GoogleAuth(CREDS, token_path=tmp_path / "t.json")
    with httpx.Client(auth=auth) as client, pytest.raises(RuntimeError, match="Async"):
        client.get(API)
