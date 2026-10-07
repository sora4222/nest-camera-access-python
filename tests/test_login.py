"""Tests for the one-time Login."""

import importlib
import socket
import threading
from typing import cast
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from googlenestcam.credentials import Credentials
from googlenestcam.login import LoginMode, login
from googlenestcam.token_store import load_refresh_token

# The package exports the login function under the same name as its module.
login_module = importlib.import_module("googlenestcam.login")

CREDENTIALS = Credentials("id", "secret", "p")


@pytest.fixture
def exchanged(monkeypatch) -> dict:
    """Pretend Google swaps any code for the refresh token "refresh"."""
    calls: dict = {}

    def fake_exchange(credentials, code, redirect_uri, client) -> str:
        calls.update(code=code, redirect_uri=redirect_uri)
        return "refresh"

    monkeypatch.setattr(login_module, "exchange_code", fake_exchange)
    return calls


def _query(url: str) -> dict[str, str]:
    return {key: values[0] for key, values in parse_qs(urlparse(url).query).items()}


def test_server_login_saves_token(exchanged, tmp_path) -> None:
    """Server login prints the URL, reads the pasted address and saves the Token."""
    shown: list[str] = []

    def paste(_: str) -> str:
        state = _query(shown[-1])["state"]
        return f"https://www.google.com/?code=abc&state={state}"

    path = login(
        "server",
        token_path=tmp_path / "token.json",
        show=shown.append,
        ask=paste,
        credentials=CREDENTIALS,
    )
    assert load_refresh_token(path) == "refresh"
    assert exchanged == {"code": "abc", "redirect_uri": "https://www.google.com"}


def test_browser_login_saves_token(exchanged, tmp_path) -> None:
    """Browser login opens the URL, catches the redirect and saves the Token."""

    def fake_browser(url: str) -> bool:
        query = _query(url)
        redirect = f"{query['redirect_uri']}/?code=abc&state={query['state']}"
        threading.Thread(target=httpx.get, args=(redirect,)).start()
        return True

    path = login(
        token_path=tmp_path / "token.json",
        port=0,
        open_url=fake_browser,
        show=lambda _: None,
        credentials=CREDENTIALS,
    )
    assert load_refresh_token(path) == "refresh"
    assert exchanged["code"] == "abc"
    assert exchanged["redirect_uri"].startswith("http://localhost:")


def test_browser_login_always_shows_url(exchanged, tmp_path) -> None:
    """The URL is shown too, so SSH tunnel users can open it themselves."""
    shown: list[str] = []

    def no_browser(url: str) -> bool:
        query = _query(url)
        redirect = f"{query['redirect_uri']}/?code=abc&state={query['state']}"
        threading.Thread(target=httpx.get, args=(redirect,)).start()
        return False

    login(
        token_path=tmp_path / "token.json",
        port=0,
        open_url=no_browser,
        show=shown.append,
        credentials=CREDENTIALS,
    )
    assert any("nestservices.google.com" in line for line in shown)


def test_unknown_mode_is_rejected(tmp_path) -> None:
    """A mistyped mode gives a clear error."""
    with pytest.raises(ValueError, match="browser"):
        login(cast(LoginMode, "other"), credentials=CREDENTIALS)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_browser_login_uses_given_redirect_uri(exchanged, tmp_path) -> None:
    """A given redirect URI is sent to Google, and the server listens on ``port``."""
    port = _free_port()
    redirect_uri = f"http://127.0.0.1:{port}/callback"

    def fake_browser(url: str) -> bool:
        query = _query(url)
        assert query["redirect_uri"] == redirect_uri
        redirect = f"{query['redirect_uri']}?code=abc&state={query['state']}"
        threading.Thread(target=httpx.get, args=(redirect,)).start()
        return True

    login(
        token_path=tmp_path / "token.json",
        port=port,
        redirect_uri=redirect_uri,
        open_url=fake_browser,
        show=lambda _: None,
        credentials=CREDENTIALS,
    )
    assert exchanged == {"code": "abc", "redirect_uri": redirect_uri}


def test_server_login_uses_given_redirect_uri(exchanged, tmp_path) -> None:
    """Server login can send Google to another web application."""
    shown: list[str] = []
    redirect_uri = "https://example.com/nest"

    def paste(_: str) -> str:
        query = _query(shown[-1])
        assert query["redirect_uri"] == redirect_uri
        return f"{redirect_uri}?code=abc&state={query['state']}"

    login(
        "server",
        redirect_uri=redirect_uri,
        token_path=tmp_path / "token.json",
        show=shown.append,
        ask=paste,
        credentials=CREDENTIALS,
    )
    assert exchanged == {"code": "abc", "redirect_uri": redirect_uri}


def test_redirect_uri_must_be_a_web_address() -> None:
    """A redirect URI that is not http or https gives a clear error."""
    with pytest.raises(ValueError, match="redirect_uri"):
        login(redirect_uri="localhost:8080", credentials=CREDENTIALS)
