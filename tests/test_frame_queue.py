"""Tests for keeping every Frame in order (Every-frame mode)."""

import threading
from datetime import UTC, datetime

import numpy as np
import pytest

from googlenestcam.errors import StreamError
from googlenestcam.frame import Frame
from googlenestcam.frame_queue import FrameQueue


def make_frame(value: int) -> Frame:
    """A tiny Frame filled with ``value``."""
    return Frame(np.full((1, 1, 3), value, dtype=np.uint8), datetime.now(UTC))


def values(queue: FrameQueue, count: int) -> list[int]:
    """Read ``count`` Frames and return their fill values."""
    frames = [queue.get() for _ in range(count)]
    return [int(frame.image[0, 0, 0]) for frame in frames if frame is not None]


def test_gives_every_frame_in_order() -> None:
    """Frames come out in the order they went in."""
    queue = FrameQueue(size=5)
    for value in (1, 2, 3):
        queue.put(make_frame(value))
    assert values(queue, 3) == [1, 2, 3]


def test_full_queue_raises_by_default() -> None:
    """When the reader is too slow, the next read raises a clear error."""
    queue = FrameQueue(size=2)
    for value in (1, 2, 3):
        queue.put(make_frame(value))
    with pytest.raises(StreamError, match=r"full.*queue_size"):
        queue.get()


def test_drop_oldest_warns_once_and_counts() -> None:
    """With drop_oldest, old Frames are dropped, counted and warned about once."""
    queue = FrameQueue(size=2, on_full="drop_oldest")
    with pytest.warns(UserWarning, match="dropp") as warned:
        for value in (1, 2, 3, 4):
            queue.put(make_frame(value))
    assert len(warned) == 1
    assert queue.dropped == 2
    assert values(queue, 2) == [3, 4]


def test_close_wakes_a_waiting_reader() -> None:
    """Closing ends a waiting read with ``None``."""
    queue = FrameQueue(size=2)
    threading.Timer(0.05, queue.close).start()
    assert queue.get() is None


def test_size_must_be_positive() -> None:
    """A queue needs room for at least one Frame."""
    with pytest.raises(ValueError, match="queue_size"):
        FrameQueue(size=0)
