"""Calls to Google's Smart Device Management (SDM) API.

The client must use ``base_url=API_URL`` and ``auth=GoogleAuth(...)``.
"""

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
    client: httpx.AsyncClient, project_id: str
) -> list[dict[str, Any]]:
    """Return every device on the account as Google describes it.

    Raises:
        GoogleApiError: If Google refuses the request.
    """
    devices: list[dict[str, Any]] = []
    params: dict[str, str] = {}
    while True:
        response = await client.get(f"enterprises/{project_id}/devices", params=params)
        _raise_for_error(response)
        body = response.json()
        devices.extend(body.get("devices", []))
        if not body.get("nextPageToken"):
            return devices
        params = {"pageToken": body["nextPageToken"]}


async def execute_command(
    client: httpx.AsyncClient,
    device_id: str,
    command: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Run a device command and return its ``results``.

    Args:
        client: HTTP client to use.
        device_id: Google's full device ID (``enterprises/.../devices/...``).
        command: Full command name, like
            ``sdm.devices.commands.CameraLiveStream.GenerateWebRtcStream``.
        params: The command's parameters.

    Raises:
        GoogleApiError: If Google refuses the command.
    """
    response = await client.post(
        f"{device_id}:executeCommand", json={"command": command, "params": params}
    )
    _raise_for_error(response)
    return response.json().get("results", {})
