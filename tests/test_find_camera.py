"""Tests for picking one Camera by name or ID."""

import pytest

from googlenestcam.camera import Camera
from googlenestcam.errors import CameraNotFoundError
from googlenestcam.find_camera import find_camera

FRONT = Camera(id="enterprises/p/devices/a", name="Front door", room="Front door")
GARDEN = Camera(id="enterprises/p/devices/b", name="Garden", room="Garden")
GARDEN_2 = Camera(id="enterprises/p/devices/c", name="Garden", room="Garden")


def test_by_name_ignores_case() -> None:
    """Names match whatever the case."""
    assert find_camera([FRONT, GARDEN], "front DOOR") is FRONT


def test_by_full_id() -> None:
    """The full Google ID matches."""
    assert find_camera([FRONT, GARDEN], "enterprises/p/devices/b") is GARDEN


def test_by_short_id() -> None:
    """The last part of the Google ID matches."""
    assert find_camera([FRONT, GARDEN], "b") is GARDEN


def test_unknown_name_lists_cameras() -> None:
    """A wrong name says which Cameras exist."""
    with pytest.raises(CameraNotFoundError, match="Front door, Garden"):
        find_camera([FRONT, GARDEN], "Kitchen")


def test_shared_name_asks_for_id() -> None:
    """Two Cameras with one name need the ID instead."""
    with pytest.raises(CameraNotFoundError, match="enterprises/p/devices/c"):
        find_camera([GARDEN, GARDEN_2], "Garden")
