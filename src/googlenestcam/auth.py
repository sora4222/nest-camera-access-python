"""Hand out fresh access tokens for Google's API, using the saved Token."""

import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

import httpx

from googlenestcam.credentials import Credentials, load_credentials
from googlenestcam.errors import MissingTokenError
from googlenestcam.login import login
from googlenestcam.oauth import AccessToken, refresh_access_token
from googlenestcam.token_store import load_refresh_token

MissingTokenAction = Literal["login", "raise"]
REFRESH_EARLY = timedelta(seconds=60)


class GoogleAuth:
    """Keeps a valid access token, refreshing it from the Token as needed."""

    def __init__(
        self,
        credentials: Credentials | None = None,
        *,
        token_path: Path | None = None,
        on_missing_token: MissingTokenAction = "login",
    ) -> None:
        """Set up access.

        Args:
            credentials: Credentials to use; loaded from the environment if
                not given.
            token_path: Where the Token is kept.
            on_missing_token: ``"login"`` starts a browser Login when there is
                no Token; ``"raise"`` raises ``MissingTokenError`` instead.
        """
        self._credentials = credentials or load_credentials()
        self._token_path = token_path
        self._on_missing_token = on_missing_token
        self._access_token: AccessToken | None = None
        self._lock = asyncio.Lock()

    async def access_token(self, client: httpx.AsyncClient) -> str:
        """Return an access token that is valid for at least a minute.

        Raises:
            MissingTokenError: If there is no Token and logging in is off.
            TokenError: If Google refuses the Token.
        """
        async with self._lock:
            token = self._access_token
            if token is None or token.expires_at - REFRESH_EARLY <= datetime.now(UTC):
                refresh_token = await self._refresh_token()
                token = await refresh_access_token(
                    self._credentials, refresh_token, client
                )
                self._access_token = token
            return token.value

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
