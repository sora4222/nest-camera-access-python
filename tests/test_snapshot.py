"""Tests for Snapshots, against the fake Google."""

import pytest

from googlenestcam.errors import SnapshotTimeoutError, StreamError
from tests.fake_google import HEIGHT, WIDTH


def test_snapshot_gives_one_frame(camera, google) -> None:
    """A Snapshot is one RGB Frame, and its Stream is stopped at Google."""
    frame = camera.snapshot()
    assert frame.image.shape == (HEIGHT, WIDTH, 3)
    assert google.command_names() == ["GenerateWebRtcStream", "StopWebRtcStream"]


def test_snapshot_times_out_clearly_and_still_stops(camera, google) -> None:
    """No Frame in time gives a clear error, and the Stream is still stopped."""
    google.send_video = False
    with pytest.raises(SnapshotTimeoutError, match=r"0\.3 seconds"):
        camera.snapshot(timeout=0.3)
    assert google.command_names()[-1] == "StopWebRtcStream"


def test_snapshot_refused_gives_a_clear_error(camera, google) -> None:
    """A refused Stream names Google's reason."""
    google.refuse_stream = "Camera is offline"
    with pytest.raises(StreamError, match="Camera is offline"):
        camera.snapshot()


async def test_snapshot_async(camera, google) -> None:
    """Async code gets a Frame the same way."""
    frame = await camera.snapshot_async()
    assert frame.image.shape == (HEIGHT, WIDTH, 3)
    assert google.command_names()[-1] == "StopWebRtcStream"
