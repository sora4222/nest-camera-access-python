"""Checks the saved Token against Google. Run with ``make test_real_cameras``."""

import httpx
import pytest

from googlenestcam import sdm
from googlenestcam.auth import GoogleAuth
from googlenestcam.credentials import load_credentials
from googlenestcam.errors import CredentialsError
from googlenestcam.token_store import load_refresh_token

pytestmark = pytest.mark.real_camera


async def test_real_token_signs_api_requests() -> None:
    """The saved Token and Credentials let Google's API list devices."""
    try:
        credentials = load_credentials()
        auth = GoogleAuth(credentials, on_missing_token="raise")
    except CredentialsError as error:
        pytest.skip(f"No Credentials: {error}")
    if not load_refresh_token():
        pytest.skip("No Token; run googlenestcam.login() first")
    async with httpx.AsyncClient(base_url=sdm.API_URL, auth=auth, timeout=20) as client:
        assert isinstance(await sdm.list_devices(client, credentials.project_id), list)
