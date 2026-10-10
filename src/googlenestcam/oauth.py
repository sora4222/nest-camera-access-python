"""Talk to Google's OAuth service for Nest Device Access."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from googlenestcam.credentials import Credentials
from googlenestcam.errors import LoginError, TokenError

AUTH_URL = "https://nestservices.google.com/partnerconnections/{project_id}/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/sdm.service"


@dataclass(frozen=True)
class AccessToken:
    """A short-lived access token for Google's API."""

    value: str
    expires_at: datetime


def authorization_url(credentials: Credentials, redirect_uri: str, state: str) -> str:
    """Return the Nest consent page URL the developer opens to log in."""
    query = urlencode(
        {
            "redirect_uri": redirect_uri,
            "access_type": "offline",
            "prompt": "consent",
            "client_id": credentials.client_id,
            "response_type": "code",
            "scope": SCOPE,
            "state": state,
        }
    )
    return AUTH_URL.format(project_id=credentials.project_id) + "?" + query


def code_from_address(address: str, expected_state: str) -> str:
    """Return the code from Google's redirect address, or a bare pasted code.

    Raises:
        LoginError: If access was denied, the state does not match, or there
            is no code.
    """
    address = address.strip()
    if "://" not in address and "=" not in address:
        if not address:
            raise LoginError("No code was given")
        return address
    query = parse_qs(urlparse(address).query)
    if "error" in query:
        raise LoginError(f"Google refused access: {query['error'][0]}")
    if "state" in query and query["state"][0] != expected_state:
        raise LoginError("This address is from a different login attempt")
    if "code" not in query:
        raise LoginError("The address has no code in it")
    return query["code"][0]


def _google_error(response: httpx.Response) -> str:
    try:
        return response.json().get("error", response.reason_phrase)
    except ValueError:
        return response.reason_phrase


def exchange_code(
    credentials: Credentials, code: str, redirect_uri: str, client: httpx.Client
) -> str:
    """Swap a Login code for the Token (refresh token).

    Raises:
        LoginError: If Google refuses the code or sends no refresh token.
    """
    response = client.post(
        TOKEN_URL,
        data={
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        },
    )
    if response.is_error:
        raise LoginError(f"Google refused the code: {_google_error(response)}")
    refresh_token = response.json().get("refresh_token")
    if not refresh_token:
        raise LoginError("Google sent no refresh token; run the login again")
    return refresh_token


def refresh_request(credentials: Credentials, refresh_token: str) -> httpx.Request:
    """Return the request that swaps the Token for a short-lived access token."""
    return httpx.Request(
        "POST",
        TOKEN_URL,
        data={
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )


def read_access_token(response: httpx.Response) -> AccessToken:
    """Return the access token from Google's reply to ``refresh_request``.

    Raises:
        TokenError: If Google refused the Token.
    """
    if response.is_error:
        raise TokenError(
            f"Google refused the Token ({_google_error(response)}); "
            "run googlenestcam.login() again"
        )
    body = response.json()
    expires_at = datetime.now(UTC) + timedelta(seconds=body["expires_in"])
    return AccessToken(body["access_token"], expires_at)
