"""Lists real Cameras. Run with ``make test_real_cameras``."""

import pytest

from googlenestcam.errors import CredentialsError
from googlenestcam.nest import Nest
from googlenestcam.token_store import load_refresh_token

pytestmark = pytest.mark.real_camera


@pytest.fixture
def nest() -> Nest:
    """A Nest for the real account, or skip if not set up."""
    try:
        nest = Nest(on_missing_token="raise")
    except CredentialsError as error:
        pytest.skip(f"No Credentials: {error}")
    if not load_refresh_token():
        pytest.skip("No Token; run make login first")
    return nest


def test_lists_real_cameras(nest) -> None:
    """The account has at least one Camera, and each can be found by name."""
    cameras = nest.list_cameras()
    assert cameras, "No WebRTC Cameras found on this account"
    for camera in cameras:
        print(f"{camera.name!r} ({camera.kind}) {camera.id}")
    assert nest.camera(cameras[0].id) == cameras[0]


def test_streams_frames_from_a_real_camera(nest) -> None:
    """A few Frames arrive from the first Camera."""
    camera = nest.list_cameras()[0]
    with camera.stream() as stream:
        frames = [frame for frame, _ in zip(stream.frames(), range(3), strict=False)]
    assert len(frames) == 3
    height, width, colours = frames[0].image.shape
    print(f"{camera.name!r}: {width}x{height} at {frames[0].time}")
    assert colours == 3
