"""Tests for the package-level shortcuts that share one default Nest."""

import googlenestcam
from googlenestcam import default_nest
from googlenestcam.camera import Camera


class FakeNest:
    """Stands in for a Nest with two Cameras."""

    def __init__(self) -> None:
        """Create the fake Cameras."""
        self.cameras = [Camera("enterprises/p/devices/a", "Front door")]

    def list_cameras(self) -> list[Camera]:
        """Return the fake Cameras."""
        return self.cameras

    def camera(self, name_or_id: str) -> Camera:
        """Return the first fake Camera."""
        return self.cameras[0]

    async def list_cameras_async(self) -> list[Camera]:
        """Return the fake Cameras."""
        return self.cameras

    async def camera_async(self, name_or_id: str) -> Camera:
        """Return the first fake Camera."""
        return self.cameras[0]


def test_shortcuts_use_the_default_nest(monkeypatch) -> None:
    """list_cameras() and camera() go to the shared default Nest."""
    fake = FakeNest()
    monkeypatch.setattr(default_nest, "_default", fake)
    assert googlenestcam.list_cameras() == fake.cameras
    assert googlenestcam.camera("Front door") is fake.cameras[0]


async def test_async_shortcuts(monkeypatch) -> None:
    """Async shortcuts go to the shared default Nest."""
    fake = FakeNest()
    monkeypatch.setattr(default_nest, "_default", fake)
    assert await googlenestcam.list_cameras_async() == fake.cameras
    assert await googlenestcam.camera_async("a") is fake.cameras[0]


def test_default_nest_is_made_once(monkeypatch) -> None:
    """The default Nest is built from the environment once and reused."""
    monkeypatch.setenv("GOOGLENESTCAM_CLIENT_ID", "id")
    monkeypatch.setenv("GOOGLENESTCAM_CLIENT_SECRET", "secret")
    monkeypatch.setenv("GOOGLENESTCAM_PROJECT_ID", "p")
    monkeypatch.setattr(default_nest, "_default", None)
    first = default_nest.get_default_nest()
    assert default_nest.get_default_nest() is first
    assert first.credentials.project_id == "p"
