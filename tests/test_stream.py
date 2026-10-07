"""Tests for live Streams, against a fake Google with a local WebRTC peer."""

import time
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from googlenestcam.errors import StreamError
from tests.fake_google import COLOUR, HEIGHT, WIDTH


def first_frames(frames: Iterator, count: int) -> list:
    """Read ``count`` Frames."""
    return [frame for frame, _ in zip(frames, range(count), strict=False)]


def test_stream_gives_rgb_frames(camera) -> None:
    """Frames are NumPy RGB pictures with a UTC receive time."""
    with camera.stream() as stream:
        frames = first_frames(stream.frames(), 3)
    assert len(frames) == 3
    for frame in frames:
        assert frame.image.shape == (HEIGHT, WIDTH, 3)
        assert frame.image.dtype == np.uint8
        assert frame.time.tzinfo is not None
        red, green, blue = frame.image[HEIGHT // 2, WIDTH // 2]
        assert abs(int(red) - COLOUR[0]) < 30 and green < 80 and blue < 80
    assert frames[0].time <= frames[1].time <= frames[2].time


def test_latest_mode_skips_old_frames(camera) -> None:
    """After a slow step, the next Frame is the newest, not an old one."""
    with camera.stream() as stream:
        frames = stream.frames()
        next(frames)
        time.sleep(0.5)
        slow_step_done = datetime.now(UTC)
        newest = next(frames)
    assert newest.time > slow_step_done - timedelta(seconds=0.2)


def test_leaving_the_block_stops_the_stream_at_google(camera, google) -> None:
    """``StopWebRtcStream`` is sent for the session when the block ends."""
    with camera.stream() as stream:
        next(stream.frames())
    assert google.commands[-1] == ("StopWebRtcStream", {"mediaSessionId": "session-1"})


def test_stream_is_stopped_after_an_error_in_the_block(camera, google) -> None:
    """An error inside the block still stops the Stream at Google."""
    with pytest.raises(ValueError), camera.stream():
        raise ValueError("my code failed")
    assert google.command_names()[-1] == "StopWebRtcStream"


def test_google_refusing_gives_a_clear_error(camera, google) -> None:
    """A refused Stream names Google's reason."""
    google.refuse_stream = "Camera is offline"
    with pytest.raises(StreamError, match="Camera is offline"), camera.stream():
        pass


def test_stream_is_extended_before_it_expires(camera, google) -> None:
    """The session is extended a minute before it expires, then keeps its new ID."""
    google.expires_in = 61
    with camera.stream() as stream:
        next(stream.frames())
        time.sleep(1.5)
        next(stream.frames())
    assert ("ExtendWebRtcStream", {"mediaSessionId": "session-1"}) in google.commands
    assert google.commands[-1] == ("StopWebRtcStream", {"mediaSessionId": "session-2"})


async def test_sync_stream_works_inside_a_running_loop(camera) -> None:
    """The sync API works where a loop already runs, as in Jupyter."""
    with camera.stream() as stream:
        assert next(stream.frames()).image.shape == (HEIGHT, WIDTH, 3)


async def test_stream_async_gives_frames(camera, google) -> None:
    """Async code gets the same Frames and stops the Stream at the end."""
    async with camera.stream_async() as stream:
        async for frame in stream.frames():
            assert frame.image.shape == (HEIGHT, WIDTH, 3)
            break
    assert google.command_names()[-1] == "StopWebRtcStream"
