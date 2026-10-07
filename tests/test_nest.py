"""Tests for listing and picking Cameras through Google's API."""

import httpx
import pytest

from googlenestcam.credentials import Credentials
from googlenestcam.errors import GoogleApiError
from googlenestcam.nest import Nest
from googlenestcam.token_store import save_refresh_token
from tests.fakes import device

CREDS = Credentials("id", "secret", "project")


@pytest.fixture
def google() -> dict:
    """Fake Google: token endpoint plus a devices list, with request log."""
    state: dict = {"devices": [device("a"), device("b", room="Garden")], "seen": []}

    def handler(request: httpx.Request) -> httpx.Response:
        state["seen"].append(request)
        if request.url.host == "oauth2.googleapis.com":
            return httpx.Response(200, json={"access_token": "a", "expires_in": 3600})
        return httpx.Response(200, json={"devices": state["devices"]})

    state["transport"] = httpx.MockTransport(handler)
    return state


@pytest.fixture
def nest(google, tmp_path) -> Nest:
    """A Nest talking to fake Google, with a saved Token."""
    path = tmp_path / "token.json"
    save_refresh_token("r", path)
    return Nest(credentials=CREDS, token_path=path, transport=google["transport"])


def test_list_cameras(nest, google) -> None:
    """Every WebRTC Camera on the account is listed."""
    cameras = nest.list_cameras()
    assert [camera.name for camera in cameras] == ["Front door", "Garden"]
    devices_request = google["seen"][-1]
    assert devices_request.url.path == "/v1/enterprises/project/devices"
    assert devices_request.headers["Authorization"] == "Bearer a"


def test_camera_by_name(nest) -> None:
    """One Camera is picked by its name."""
    assert nest.camera("garden").id == "enterprises/project/devices/b"


async def test_async_versions(nest) -> None:
    """Async code can await the same calls."""
    cameras = await nest.list_cameras_async()
    assert len(cameras) == 2
    camera = await nest.camera_async("Front door")
    assert camera.name == "Front door"


def test_google_error_is_clear(nest, google) -> None:
    """A refused request names the status and Google's message."""

    def refuse(request: httpx.Request) -> httpx.Response:
        if request.url.host == "oauth2.googleapis.com":
            return httpx.Response(200, json={"access_token": "a", "expires_in": 3600})
        return httpx.Response(403, json={"error": {"message": "No access"}})

    nest_refused = Nest(
        credentials=CREDS,
        token_path=nest.token_path,
        transport=httpx.MockTransport(refuse),
    )
    with pytest.raises(GoogleApiError, match=r"403.*No access"):
        nest_refused.list_cameras()
