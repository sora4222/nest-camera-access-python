"""The shared default Nest behind the package-level shortcuts."""

import threading

from googlenestcam.camera import Camera
from googlenestcam.nest import Nest

_default: Nest | None = None
_lock = threading.Lock()


def get_default_nest() -> Nest:
    """Return the default Nest, built once from environment variables."""
    global _default
    with _lock:
        if _default is None:
            _default = Nest()
        return _default


def list_cameras() -> list[Camera]:
    """Return every Camera on the account that streams over WebRTC."""
    return get_default_nest().list_cameras()


async def list_cameras_async() -> list[Camera]:
    """Async version of ``list_cameras``."""
    return await get_default_nest().list_cameras_async()


def camera(name_or_id: str) -> Camera:
    """Return one Camera by its Google Home name (any case) or Google ID."""
    return get_default_nest().camera(name_or_id)


async def camera_async(name_or_id: str) -> Camera:
    """Async version of ``camera``."""
    return await get_default_nest().camera_async(name_or_id)
