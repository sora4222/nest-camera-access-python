"""A Camera on the developer's Google account."""

from dataclasses import dataclass, field
from functools import partial
from typing import TYPE_CHECKING, Any, Self

from googlenestcam.stream import AsyncStream, Stream
from googlenestcam.webrtc_session import RunCommand

if TYPE_CHECKING:
    from googlenestcam.nest import Nest

LIVE_STREAM_TRAIT = "sdm.devices.traits.CameraLiveStream"
INFO_TRAIT = "sdm.devices.traits.Info"
TYPE_PREFIX = "sdm.devices.types."


@dataclass(frozen=True)
class Camera:
    """A Google Nest camera or doorbell that streams over WebRTC.

    Attributes:
        id: Google's full device ID (``enterprises/.../devices/...``).
        name: The name shown in the Google Home app, or the room name.
        room: The room the Camera is in, or ``""``.
        kind: ``"camera"``, ``"doorbell"`` or ``"display"``.
    """

    id: str
    name: str
    room: str = ""
    kind: str = "camera"
    nest: "Nest | None" = field(default=None, repr=False, compare=False)

    @classmethod
    def from_device(
        cls, device: dict[str, Any], nest: "Nest | None" = None
    ) -> Self | None:
        """Build a Camera from Google's device data, or ``None`` if it is not one."""
        traits = device.get("traits", {})
        protocols = traits.get(LIVE_STREAM_TRAIT, {}).get("supportedProtocols", [])
        if "WEB_RTC" not in protocols:
            return None
        device_id = device["name"]
        relations = device.get("parentRelations") or [{}]
        room = relations[0].get("displayName", "")
        custom_name = traits.get(INFO_TRAIT, {}).get("customName", "")
        return cls(
            id=device_id,
            name=custom_name or room or device_id.rsplit("/", 1)[-1],
            room=room,
            kind=device.get("type", "").removeprefix(TYPE_PREFIX).lower() or "camera",
            nest=nest,
        )

    def stream(self) -> Stream:
        """Open a live Stream in Latest mode; use it in a ``with`` block.

        Example::

            with camera.stream() as stream:
                for frame in stream.frames():
                    model(frame.image)
        """
        return Stream(self._run_command())

    def stream_async(self) -> AsyncStream:
        """Async version of ``stream``; use it in an ``async with`` block."""
        return AsyncStream(self._run_command())

    def _run_command(self) -> RunCommand:
        if self.nest is None:
            raise RuntimeError("Get Cameras from list_cameras() or camera() to stream")
        return partial(self.nest._execute_command, self.id)
