"""Take one Frame by briefly opening a Stream (a Snapshot)."""

import asyncio

from googlenestcam.errors import SnapshotTimeoutError, StreamError
from googlenestcam.frame import Frame
from googlenestcam.latest_frame import LatestFrame
from googlenestcam.webrtc_session import RunCommand, WebRtcSession


# The timeout only covers waiting for the Frame, so it matches snapshot().
async def take_snapshot(run_command: RunCommand, timeout: float) -> Frame:  # noqa: ASYNC109
    """Open a Stream, wait for its first Frame, and always stop it.

    Runs on the background loop.

    Raises:
        SnapshotTimeoutError: If no Frame arrives within ``timeout`` seconds
            of the Stream starting.
        StreamError: If Google refuses or the Stream fails.
    """
    frames = LatestFrame()
    session = WebRtcSession(run_command, on_frame=frames.put, on_error=frames.fail)
    await session.start()
    try:
        frame = await asyncio.wait_for(asyncio.to_thread(frames.get), timeout)
    except TimeoutError:
        raise SnapshotTimeoutError(
            f"No Frame arrived within {timeout:g} seconds; try a longer timeout"
        ) from None
    finally:
        frames.close()
        await session.close()
    if frame is None:
        raise StreamError("The Stream closed before a Frame arrived")
    return frame
