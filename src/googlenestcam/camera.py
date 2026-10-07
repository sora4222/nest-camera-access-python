"""A Camera on the developer's Google account."""

from dataclasses import dataclass, field
from functools import partial
from typing import TYPE_CHECKING, Any, Self

from googlenestcam import background_loop
from googlenestcam.frame import Frame
from googlenestcam.snapshot import take_snapshot
from googlenestcam.frame_queue import OnFull
from googlenestcam.stream import AsyncStream, FrameMode, Stream
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

    def snapshot(self, timeout: float = 20) -> Frame:
        """Take one Frame.

        This is slow: it starts a Stream, waits for one Frame and stops it.
        Open a ``stream()`` when you need many Frames.

        Args:
            timeout: Seconds to wait for the Frame once the Stream starts.

        Raises:
            SnapshotTimeoutError: If no Frame arrives in time.
            StreamError: If Google refuses to stream.
        """
        return background_loop.run(take_snapshot(self._run_command(), timeout))

    async def snapshot_async(self, timeout: float = 20) -> Frame:  # noqa: ASYNC109
        """Async version of ``snapshot``."""
        return await background_loop.run_async(
            take_snapshot(self._run_command(), timeout)
        )

    def stream(
        self,
        frames: FrameMode = "latest",
        *,
        queue_size: int = 100,
        on_full: OnFull = "raise",
        retries: int = 3,
    ) -> Stream:
        """Open a live Stream; use it in a ``with`` block.

        Example::

            with camera.stream() as stream:
                for frame in stream.frames():
                    model(frame.image)

        Args:
            frames: ``"latest"`` gives the newest Frame and skips ones you were
                too slow for. ``"all"`` gives every Frame in order.
            queue_size: In ``"all"`` mode, the most Frames kept unread.
            on_full: In ``"all"`` mode, what happens when the queue is full:
                ``"raise"`` makes ``frames()`` raise ``StreamError``;
                ``"drop_oldest"`` drops the oldest, warns once and counts in
                ``stream.dropped``.
            retries: How many times in a row to reconnect after the
                connection drops. After the last failed try, ``frames()``
                raises ``StreamError``.
        """
        return Stream(self._run_command(), frames, queue_size, on_full, retries)

    def stream_async(
        self,
        frames: FrameMode = "latest",
        *,
        queue_size: int = 100,
        on_full: OnFull = "raise",
        retries: int = 3,
    ) -> AsyncStream:
        """Async version of ``stream``; use it in an ``async with`` block."""
        return AsyncStream(self._run_command(), frames, queue_size, on_full, retries)

    def _run_command(self) -> RunCommand:
        if self.nest is None:
            raise RuntimeError("Get Cameras from list_cameras() or camera() to stream")
        return partial(self.nest._execute_command, self.id)
