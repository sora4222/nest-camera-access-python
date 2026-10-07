"""Tests for keeping only the newest Frame."""

import threading
from datetime import UTC, datetime

import numpy as np
import pytest

from googlenestcam.errors import StreamError
from googlenestcam.latest_frame import LatestFrame


def make_frame(value: int):
    """A tiny Frame filled with ``value``."""
    from googlenestcam.frame import Frame

    return Frame(np.full((1, 1, 3), value, dtype=np.uint8), datetime.now(UTC))


def test_gives_only_the_newest_frame() -> None:
    """Older unread Frames are replaced by newer ones."""
    latest = LatestFrame()
    for value in (1, 2, 3):
        latest.put(make_frame(value))
    frame = latest.get()
    assert frame is not None
    assert frame.image[0, 0, 0] == 3


def test_waits_for_a_new_frame() -> None:
    """A reader waits until a Frame newer than the last one arrives."""
    latest = LatestFrame()
    latest.put(make_frame(1))
    latest.get()
    threading.Timer(0.05, latest.put, [make_frame(2)]).start()
    frame = latest.get()
    assert frame is not None
    assert frame.image[0, 0, 0] == 2


def test_close_wakes_a_waiting_reader() -> None:
    """Closing ends a waiting read with ``None``."""
    latest = LatestFrame()
    threading.Timer(0.05, latest.close).start()
    assert latest.get() is None


def test_failure_is_raised_to_the_reader() -> None:
    """An error from the Stream is raised from ``get``."""
    latest = LatestFrame()
    latest.fail(StreamError("dropped"))
    with pytest.raises(StreamError, match="dropped"):
        latest.get()
