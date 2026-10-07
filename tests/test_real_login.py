"""Checks the saved Token against Google. Run with ``make test_real_cameras``."""

import httpx
import pytest

from googlenestcam.auth import GoogleAuth
from googlenestcam.errors import CredentialsError
from googlenestcam.token_store import load_refresh_token

pytestmark = pytest.mark.real_camera


async def test_real_token_gives_access_token() -> None:
    """The saved Token and Credentials get an access token from Google."""
    try:
        auth = GoogleAuth(on_missing_token="raise")
    except CredentialsError as error:
        pytest.skip(f"No Credentials: {error}")
    if not load_refresh_token():
        pytest.skip("No Token; run googlenestcam.login() first")
    async with httpx.AsyncClient(timeout=20) as client:
        assert await auth.access_token(client)
