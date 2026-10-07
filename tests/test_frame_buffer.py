"""Tests for the Frame buffer behind Latest mode and Every-frame mode."""

import logging
import threading
from datetime import UTC, datetime

import numpy as np
import pytest

from googlenestcam.errors import StreamError
from googlenestcam.frame import Frame
from googlenestcam.frame_buffer import FrameBuffer


def make_frame(value: int) -> Frame:
    """A tiny Frame filled with ``value``."""
    return Frame(np.full((1, 1, 3), value, dtype=np.uint8), datetime.now(UTC))


def values(buffer: FrameBuffer, count: int) -> list[int]:
    """Read ``count`` Frames and return their fill values."""
    frames = [buffer.get() for _ in range(count)]
    return [int(frame.image[0, 0, 0]) for frame in frames if frame is not None]


# Latest mode


def test_latest_gives_only_the_newest_frame(caplog: pytest.LogCaptureFixture) -> None:
    """Older unread Frames are replaced by newer ones, quietly."""
    buffer = FrameBuffer.latest()
    with caplog.at_level(logging.DEBUG, logger="googlenestcam"):
        for value in (1, 2, 3):
            buffer.put(make_frame(value))
    assert values(buffer, 1) == [3]
    assert buffer.dropped == 0
    assert caplog.records == []


def test_latest_waits_for_a_new_frame() -> None:
    """A reader waits until a Frame newer than the last one arrives."""
    buffer = FrameBuffer.latest()
    buffer.put(make_frame(1))
    buffer.get()
    threading.Timer(0.05, buffer.put, [make_frame(2)]).start()
    assert values(buffer, 1) == [2]


# Every-frame mode


def test_gives_every_frame_in_order() -> None:
    """Frames come out in the order they went in."""
    buffer = FrameBuffer(size=5)
    for value in (1, 2, 3):
        buffer.put(make_frame(value))
    assert values(buffer, 3) == [1, 2, 3]


def test_full_buffer_raises_by_default() -> None:
    """When the reader is too slow, the next read raises a clear error."""
    buffer = FrameBuffer(size=2)
    for value in (1, 2, 3):
        buffer.put(make_frame(value))
    with pytest.raises(StreamError, match=r"full.*queue_size"):
        buffer.get()


def test_drop_oldest_logs_and_counts(caplog: pytest.LogCaptureFixture) -> None:
    """With drop_oldest, the first drop logs a warning and later ones log debug."""
    buffer = FrameBuffer(size=2, on_full="drop_oldest")
    with caplog.at_level(logging.DEBUG, logger="googlenestcam"):
        for value in (1, 2, 3, 4):
            buffer.put(make_frame(value))
    assert [r.levelno for r in caplog.records] == [logging.WARNING, logging.DEBUG]
    assert "dropp" in caplog.records[0].getMessage()
    assert buffer.dropped == 2
    assert values(buffer, 2) == [3, 4]


def test_drop_logs_follow_the_developers_logging_level(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Drop logs go through the ``googlenestcam`` logger, so its level applies."""
    buffer = FrameBuffer(size=1, on_full="drop_oldest")
    with caplog.at_level(logging.ERROR, logger="googlenestcam"):
        buffer.put(make_frame(1))
        buffer.put(make_frame(2))
    assert caplog.records == []
    assert buffer.dropped == 1


def test_size_must_be_positive() -> None:
    """A buffer needs room for at least one Frame."""
    with pytest.raises(ValueError, match="queue_size"):
        FrameBuffer(size=0)


def test_on_full_must_be_known() -> None:
    """A typo in ``on_full`` fails early."""
    with pytest.raises(ValueError, match="on_full"):
        FrameBuffer(size=2, on_full="ignore")  # ty: ignore[invalid-argument-type]


# Both modes


def test_close_wakes_a_waiting_reader() -> None:
    """Closing ends a waiting read with ``None``."""
    buffer = FrameBuffer.latest()
    threading.Timer(0.05, buffer.close).start()
    assert buffer.get() is None


def test_failure_is_raised_to_the_reader() -> None:
    """An error from the Stream is raised from ``get``."""
    buffer = FrameBuffer(size=2)
    buffer.fail(StreamError("dropped"))
    with pytest.raises(StreamError, match="dropped"):
        buffer.get()
