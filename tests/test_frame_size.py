"""Tests for resizing Frames with ``size=``, against the fake Google."""

from datetime import UTC, datetime

import pytest

from googlenestcam import background_loop
from tests.fake_google import COLOUR, HEIGHT, WIDTH

SIZE = (32, 16)


def assert_red_and_small(image) -> None:
    """The picture has the asked size and is still the fake red."""
    assert image.shape == (SIZE[1], SIZE[0], 3)
    red, green, blue = image[SIZE[1] // 2, SIZE[0] // 2]
    assert abs(int(red) - COLOUR[0]) < 30 and green < 80 and blue < 80


def test_stream_resizes_frames(camera) -> None:
    """Every Frame has the asked width and height."""
    with camera.stream(size=SIZE) as stream:
        assert_red_and_small(next(stream.frames()).image)


def test_every_frame_mode_resizes_frames(camera) -> None:
    """Every-frame mode resizes too."""
    with camera.stream("all", size=SIZE) as stream:
        assert_red_and_small(next(stream.frames()).image)


def test_resize_survives_a_reconnect(camera, google) -> None:
    """Frames after a reconnect keep the asked size."""
    with camera.stream(size=SIZE) as stream:
        frames = stream.frames()
        next(frames)
        dropped_at = datetime.now(UTC)
        background_loop.run(google.drop())
        frame = next(frames)
        while frame.time < dropped_at:
            frame = next(frames)
    assert google.generate_count() == 2
    assert_red_and_small(frame.image)


def test_no_size_keeps_the_camera_size(camera) -> None:
    """Without ``size`` Frames come at the Camera's size."""
    with camera.stream() as stream:
        assert next(stream.frames()).image.shape == (HEIGHT, WIDTH, 3)


def test_snapshot_resizes(camera) -> None:
    """A Snapshot has the asked size."""
    assert_red_and_small(camera.snapshot(size=SIZE).image)


async def test_async_calls_resize(camera) -> None:
    """``snapshot_async`` and ``stream_async`` take ``size`` too."""
    assert_red_and_small((await camera.snapshot_async(size=SIZE)).image)
    async with camera.stream_async(size=SIZE) as stream:
        async for frame in stream.frames():
            assert_red_and_small(frame.image)
            break


@pytest.mark.parametrize("size", [(0, 10), (10, -1), (10.5, 10), (10,), "640x360"])
def test_bad_size_is_a_clear_error(camera, google, size) -> None:
    """A bad size raises before any Stream starts."""
    with pytest.raises(ValueError, match="size"):
        camera.stream(size=size)
    with pytest.raises(ValueError, match="size"):
        camera.snapshot(size=size)
    assert google.generate_count() == 0
