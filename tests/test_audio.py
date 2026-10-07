"""Tests for Audio on a Stream, against the fake Google."""

import threading

import numpy as np
import pytest

from googlenestcam.audio_chunk import SAMPLE_RATE


def first(items, count: int) -> list:
    """Read ``count`` items."""
    return [item for item, _ in zip(items, range(count), strict=False)]


def test_audio_is_on_by_default(camera) -> None:
    """Audio chunks have int16 samples at 48 kHz and a UTC time."""
    with camera.stream() as stream:
        chunks = first(stream.audio(), 3)
    assert len(chunks) == 3
    for chunk in chunks:
        assert chunk.samples.dtype == np.int16
        assert chunk.samples.shape == (960, 2)  # 20 ms of stereo at 48 kHz
        assert chunk.sample_rate == SAMPLE_RATE
        assert chunk.time.tzinfo is not None


def test_frames_and_audio_from_two_threads(camera) -> None:
    """``frames()`` and ``audio()`` can be read at the same time."""
    with camera.stream() as stream:
        frames: list = []
        reader = threading.Thread(
            target=lambda: frames.extend(first(stream.frames(), 5))
        )
        reader.start()
        chunks = first(stream.audio(), 5)
        reader.join(timeout=10)
    assert len(frames) == 5
    assert len(chunks) == 5
    # Frame and Audio times are on the same clock.
    gap = abs((frames[0].time - chunks[0].time).total_seconds())
    assert gap < 5


def test_audio_can_be_turned_off(camera) -> None:
    """With ``audio=False``, Frames still come and ``audio()`` says it is off."""
    with camera.stream(audio=False) as stream:
        assert first(stream.frames(), 1)
        with pytest.raises(ValueError, match="audio=False"):
            next(stream.audio())


async def test_stream_async_has_audio(camera) -> None:
    """Async code gets Audio the same way."""
    async with camera.stream_async() as stream:
        async for chunk in stream.audio():
            assert chunk.samples.dtype == np.int16
            break
