"""Tests for keeping the last few seconds of Audio."""

import threading
from datetime import UTC, datetime

import numpy as np
import pytest

from googlenestcam.audio_buffer import AudioBuffer
from googlenestcam.audio_chunk import SAMPLE_RATE, AudioChunk
from googlenestcam.errors import StreamError


def make_chunk(value: int) -> AudioChunk:
    """A 20 ms stereo chunk filled with ``value``."""
    samples = np.full((960, 2), value, dtype=np.int16)
    return AudioChunk(samples, datetime.now(UTC))


def test_chunk_has_samples_rate_and_time() -> None:
    """A chunk knows its samples, sample rate and receive time."""
    chunk = make_chunk(3)
    assert chunk.samples.shape == (960, 2)
    assert chunk.sample_rate == SAMPLE_RATE == 48_000
    assert chunk.time.tzinfo is not None


def test_gives_chunks_in_order() -> None:
    """Chunks come out in the order they went in."""
    buffer = AudioBuffer(seconds=1)
    for value in (1, 2, 3):
        buffer.put(make_chunk(value))
    got = [buffer.get() for _ in range(3)]
    assert [int(chunk.samples[0, 0]) for chunk in got if chunk] == [1, 2, 3]


def test_unread_audio_is_bounded() -> None:
    """Only the last few seconds are kept; the oldest chunks are dropped."""
    buffer = AudioBuffer(seconds=1)
    for value in range(200):
        buffer.put(make_chunk(value % 100))
    first = buffer.get()
    assert first is not None
    assert int(first.samples[0, 0]) == 50  # 200 chunks put, last 50 (1 s) kept


def test_close_wakes_a_waiting_reader() -> None:
    """Closing ends a waiting read with ``None``."""
    buffer = AudioBuffer()
    threading.Timer(0.05, buffer.close).start()
    assert buffer.get() is None


def test_failure_is_raised_to_the_reader() -> None:
    """An error from the Stream is raised from ``get``."""
    buffer = AudioBuffer()
    buffer.fail(StreamError("dropped"))
    with pytest.raises(StreamError, match="dropped"):
        buffer.get()
