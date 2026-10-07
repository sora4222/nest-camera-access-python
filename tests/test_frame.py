"""Tests for Frames."""

from datetime import UTC, datetime

import numpy as np
import pytest

from googlenestcam.frame import Frame


def test_frame_has_image_and_time() -> None:
    """A Frame keeps its picture and when it arrived."""
    image = np.zeros((4, 6, 3), dtype=np.uint8)
    time = datetime.now(UTC)
    frame = Frame(image, time)
    assert frame.image is image
    assert frame.time == time


def test_frame_works_as_an_array() -> None:
    """``np.asarray(frame)`` gives the picture."""
    image = np.full((2, 2, 3), 7, dtype=np.uint8)
    array = np.asarray(Frame(image, datetime.now(UTC)))
    assert array.shape == (2, 2, 3)
    assert array[0, 0, 0] == 7


def test_frame_is_frozen() -> None:
    """A Frame cannot be changed after it is made."""
    frame = Frame(np.zeros((1, 1, 3), dtype=np.uint8), datetime.now(UTC))
    with pytest.raises(AttributeError):
        frame.time = datetime.now(UTC)  # type: ignore[misc]
