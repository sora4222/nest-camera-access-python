"""Pick one Camera by its name or Google ID."""

from collections.abc import Sequence

from googlenestcam.camera import Camera
from googlenestcam.errors import CameraNotFoundError


def find_camera(cameras: Sequence[Camera], name_or_id: str) -> Camera:
    """Return the Camera whose name (any case), full ID or short ID matches.

    Raises:
        CameraNotFoundError: If none match, or several share the name.
    """
    wanted = name_or_id.strip()
    for camera in cameras:
        if wanted in (camera.id, camera.id.rsplit("/", 1)[-1]):
            return camera
    matches = [
        camera for camera in cameras if camera.name.casefold() == wanted.casefold()
    ]
    if len(matches) == 1:
        return matches[0]
    if matches:
        ids = ", ".join(camera.id for camera in matches)
        raise CameraNotFoundError(
            f'Several Cameras are named "{wanted}"; use an ID: {ids}'
        )
    names = ", ".join(camera.name for camera in cameras) or "none"
    raise CameraNotFoundError(f'No Camera named "{wanted}". Cameras: {names}')
