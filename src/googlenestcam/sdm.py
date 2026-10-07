"""Calls to Google's Smart Device Management (SDM) API."""

from typing import Any

import httpx

from googlenestcam.errors import GoogleApiError

API_URL = "https://smartdevicemanagement.googleapis.com/v1"


def _raise_for_error(response: httpx.Response) -> None:
    if not response.is_error:
        return
    try:
        message = response.json()["error"]["message"]
    except (ValueError, KeyError, TypeError):
        message = response.reason_phrase
    raise GoogleApiError(f"Google API error {response.status_code}: {message}")


async def list_devices(
    client: httpx.AsyncClient, access_token: str, project_id: str
) -> list[dict[str, Any]]:
    """Return every device on the account as Google describes it.

    Raises:
        GoogleApiError: If Google refuses the request.
    """
    devices: list[dict[str, Any]] = []
    params: dict[str, str] = {}
    while True:
        response = await client.get(
            f"{API_URL}/enterprises/{project_id}/devices",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
        )
        _raise_for_error(response)
        body = response.json()
        devices.extend(body.get("devices", []))
        if not body.get("nextPageToken"):
            return devices
        params = {"pageToken": body["nextPageToken"]}
