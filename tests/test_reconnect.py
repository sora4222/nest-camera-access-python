"""Tests for Streams reconnecting after a drop, against the fake Google."""

from datetime import UTC, datetime

import pytest

from googlenestcam import background_loop
from googlenestcam.errors import CameraOffError, StreamError


def test_stream_reconnects_after_a_drop(camera, google) -> None:
    """After a drop, new Frames come in the same loop and the old session stops."""
    with camera.stream() as stream:
        frames = stream.frames()
        next(frames)
        dropped_at = datetime.now(UTC)
        background_loop.run(google.drop())
        frame = next(frames)
        while frame.time < dropped_at:
            frame = next(frames)
    assert google.generate_count() == 2
    assert ("StopWebRtcStream", {"mediaSessionId": "session-1"}) in google.commands
    assert google.commands[-1] == ("StopWebRtcStream", {"mediaSessionId": "session-2"})


def test_stream_gives_up_after_the_last_try(camera, google) -> None:
    """When every try fails, ``frames()`` raises a clear error."""
    with camera.stream(retries=2) as stream:
        frames = stream.frames()
        next(frames)
        google.refuse_stream = "Camera is offline"
        background_loop.run(google.drop())
        with pytest.raises(StreamError, match=r"2 tries.*Camera is offline"):
            for _ in frames:
                pass
    assert google.generate_count() == 3


def test_no_retries_fails_at_once(camera, google) -> None:
    """With ``retries=0`` a drop is raised straight away."""
    with camera.stream(retries=0) as stream:
        frames = stream.frames()
        next(frames)
        background_loop.run(google.drop())
        with pytest.raises(StreamError):
            for _ in frames:
                pass
    assert google.generate_count() == 1


def test_camera_turned_off_mid_stream_gives_camera_off_error(camera, google) -> None:
    """When the Camera is turned off and stays off, the last error says so."""
    with camera.stream(retries=1) as stream:
        frames = stream.frames()
        next(frames)
        google.refuse_stream = "The camera is not available for streaming."
        background_loop.run(google.drop())
        with pytest.raises(CameraOffError, match=r"1 tries.*Google Home app"):
            for _ in frames:
                pass
