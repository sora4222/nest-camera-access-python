"""Tests for the thread-safe buffer shared by Frames and Audio."""

import threading

import pytest

from googlenestcam.errors import StreamError
from googlenestcam.media_buffer import MediaBuffer


def test_gives_items_in_order() -> None:
    """Items come out in the order they went in."""
    buffer = MediaBuffer[str](3)
    for item in "abc":
        buffer.put(item)
    assert [buffer.get() for _ in range(3)] == ["a", "b", "c"]


def test_full_buffer_drops_the_oldest() -> None:
    """When full, a new item pushes out the oldest unread one."""
    buffer = MediaBuffer[str](2)
    for item in "abc":
        buffer.put(item)
    assert [buffer.get(), buffer.get()] == ["b", "c"]


def test_size_must_be_at_least_one() -> None:
    """A buffer that can hold nothing is refused."""
    with pytest.raises(ValueError, match="at least 1"):
        MediaBuffer[str](0)


def test_close_wakes_a_waiting_reader() -> None:
    """Closing ends a waiting read with ``None``."""
    buffer = MediaBuffer[str](1)
    threading.Timer(0.05, buffer.close).start()
    assert buffer.get() is None


def test_failure_is_raised_to_the_reader() -> None:
    """An error from the Stream is raised from ``get``."""
    buffer = MediaBuffer[str](1)
    buffer.put("a")
    buffer.fail(StreamError("dropped"))
    with pytest.raises(StreamError, match="dropped"):
        buffer.get()
