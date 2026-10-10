"""Tests for talking to Google's OAuth service."""

from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from googlenestcam.credentials import Credentials
from googlenestcam.errors import LoginError, TokenError
from googlenestcam.oauth import (
    authorization_url,
    code_from_address,
    exchange_code,
    read_access_token,
    refresh_request,
)

CREDS = Credentials("client-id", "client-secret", "project")


def test_authorization_url_asks_for_offline_nest_access() -> None:
    """The URL opens the Nest consent page and asks for a refresh token."""
    url = urlparse(authorization_url(CREDS, "https://www.google.com", "state1"))
    query = parse_qs(url.query)
    assert url.netloc == "nestservices.google.com"
    assert url.path == "/partnerconnections/project/auth"
    assert query["client_id"] == ["client-id"]
    assert query["redirect_uri"] == ["https://www.google.com"]
    assert query["scope"] == ["https://www.googleapis.com/auth/sdm.service"]
    assert query["access_type"] == ["offline"]
    assert query["prompt"] == ["consent"]
    assert query["state"] == ["state1"]


def test_code_from_full_address() -> None:
    """The code is read from a pasted address."""
    address = "https://www.google.com/?code=abc&state=s&scope=x"
    assert code_from_address(address, "s") == "abc"


def test_code_from_bare_code() -> None:
    """A pasted bare code is accepted."""
    assert code_from_address("  abc  ", "s") == "abc"


def test_wrong_state_is_rejected() -> None:
    """An address from a different login attempt is refused."""
    with pytest.raises(LoginError, match="different login"):
        code_from_address("https://www.google.com/?code=abc&state=bad", "s")


def test_denied_access_is_reported() -> None:
    """If the developer said no on Google's page, the error says so."""
    with pytest.raises(LoginError, match="access_denied"):
        code_from_address("http://localhost:8080/?error=access_denied", "s")


def test_address_without_code_is_rejected() -> None:
    """An address with no code gives a clear error."""
    with pytest.raises(LoginError, match="code"):
        code_from_address("https://www.google.com/?state=s", "s")


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_exchange_code_returns_refresh_token() -> None:
    """Swapping the code gives the refresh token."""
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(parse_qs(request.content.decode()))
        return httpx.Response(200, json={"refresh_token": "r", "access_token": "a"})

    token = exchange_code(CREDS, "abc", "https://www.google.com", _client(handler))
    assert token == "r"
    assert seen["grant_type"] == ["authorization_code"]
    assert seen["code"] == ["abc"]


def test_exchange_code_rejected_by_google() -> None:
    """A refused code gives a LoginError with Google's reason."""

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": "invalid_grant"})

    with pytest.raises(LoginError, match="invalid_grant"):
        exchange_code(CREDS, "abc", "https://www.google.com", _client(handler))


def test_exchange_code_without_refresh_token() -> None:
    """Google sometimes leaves out the refresh token; that is an error."""

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"access_token": "a"})

    with pytest.raises(LoginError, match="refresh token"):
        exchange_code(CREDS, "abc", "https://www.google.com", _client(handler))


def test_refresh_request() -> None:
    """The refresh request swaps the Token at Google's token address."""
    request = refresh_request(CREDS, "r")
    assert request.method == "POST"
    assert str(request.url) == "https://oauth2.googleapis.com/token"
    form = parse_qs(request.content.decode())
    assert form["refresh_token"] == ["r"]
    assert form["grant_type"] == ["refresh_token"]
    assert form["client_id"] == ["client-id"]


def test_read_access_token() -> None:
    """Google's reply gives a short-lived access token and its expiry."""
    response = httpx.Response(200, json={"access_token": "a", "expires_in": 3599})
    token = read_access_token(response)
    assert token.value == "a"
    expected = datetime.now(UTC) + timedelta(seconds=3599)
    assert abs((token.expires_at - expected).total_seconds()) < 5


def test_revoked_refresh_token_says_login_again() -> None:
    """A revoked Token tells the developer to log in again."""
    response = httpx.Response(400, json={"error": "invalid_grant"})
    with pytest.raises(TokenError, match="login"):
        read_access_token(response)
