"""Tests for turning Google devices into Cameras."""

from googlenestcam.camera import Camera
from tests.fakes import device


def test_webrtc_camera_is_a_camera() -> None:
    """A WebRTC device becomes a Camera named after its room."""
    camera = Camera.from_device(device())
    assert camera is not None
    assert camera.name == "Front door"
    assert camera.id == "enterprises/project/devices/cam1"
    assert camera.room == "Front door"
    assert camera.kind == "camera"


def test_custom_name_wins_over_room() -> None:
    """A name set in the Google Home app wins over the room name."""
    camera = Camera.from_device(device(custom_name="Porch", kind="DOORBELL"))
    assert camera is not None
    assert camera.name == "Porch"
    assert camera.kind == "doorbell"


def test_rtsp_only_devices_are_not_cameras() -> None:
    """Older RTSP-only cameras are left out."""
    assert Camera.from_device(device(protocols=("RTSP",))) is None


def test_devices_without_live_stream_are_not_cameras() -> None:
    """Thermostats and other devices are left out."""
    thermostat = {"name": "enterprises/p/devices/t", "type": "x", "traits": {}}
    assert Camera.from_device(thermostat) is None


def test_device_without_names_uses_its_id() -> None:
    """With no custom name or room, the name is the short Google ID."""
    raw = device(room="")
    raw["parentRelations"] = []
    camera = Camera.from_device(raw)
    assert camera is not None
    assert camera.name == "cam1"
