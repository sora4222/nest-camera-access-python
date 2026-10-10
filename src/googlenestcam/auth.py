"""Sign Google API requests with a fresh access token, made from the saved Token.

``GoogleAuth`` is an ``httpx.Auth``: give it to an ``httpx.AsyncClient`` and
every request gets a ``Bearer`` header. It refreshes through the same client,
so tests and proxies see the token request too.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime, timedelta
from typing import Literal

import httpx

from googlenestcam.credentials import Credentials, load_credentials
from googlenestcam.errors import MissingTokenError
from googlenestcam.login import login
from googlenestcam.oauth import AccessToken, read_access_token, refresh_request
from googlenestcam.token_store import TokenPath, load_refresh_token

MissingTokenAction = Literal["login", "raise"]
REFRESH_EARLY = timedelta(seconds=60)


class GoogleAuth(httpx.Auth):
    """Keeps a valid access token, refreshing it from the Token as needed."""

    requires_response_body = True

    def __init__(
        self,
        credentials: Credentials | None = None,
        *,
        token_path: TokenPath | None = None,
        on_missing_token: MissingTokenAction = "login",
    ) -> None:
        """Set up access.

        Args:
            credentials: Credentials to use; loaded from the environment if
                not given.
            token_path: Where the Token is kept; see ``find_token_path``.
            on_missing_token: ``"login"`` starts a browser Login when there is
                no Token; ``"raise"`` raises ``MissingTokenError`` instead.
        """
        self._credentials = credentials or load_credentials()
        self._token_path = token_path
        self._on_missing_token = on_missing_token
        self._access_token: AccessToken | None = None
        self._lock = asyncio.Lock()

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        """Add the access token, first refreshing it if it expires within a minute.

        Raises:
            MissingTokenError: If there is no Token and logging in is off.
            TokenError: If Google refuses the Token.
        """
        async with self._lock:
            token = self._access_token
            if token is None or token.expires_at - REFRESH_EARLY <= datetime.now(UTC):
                refresh_token = await self._refresh_token()
                response = yield refresh_request(self._credentials, refresh_token)
                token = self._access_token = read_access_token(response)
        request.headers["Authorization"] = f"Bearer {token.value}"
        yield request

    def sync_auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response]:
        """Refuse plain ``httpx.Client``; the refresh needs ``AsyncClient``."""
        raise RuntimeError("GoogleAuth works only with httpx.AsyncClient")
        yield request  # Makes this a generator, as httpx expects.

    async def _refresh_token(self) -> str:
        refresh_token = load_refresh_token(self._token_path)
        if refresh_token:
            return refresh_token
        if self._on_missing_token == "raise":
            raise MissingTokenError("No Token found; run googlenestcam.login() first")
        await asyncio.to_thread(
            login, credentials=self._credentials, token_path=self._token_path
        )
        refresh_token = load_refresh_token(self._token_path)
        if not refresh_token:
            raise MissingTokenError("Login finished but no Token was saved")
        return refresh_token
