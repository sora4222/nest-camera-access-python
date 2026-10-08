"""One live WebRTC session with Google for one Camera.

Runs on the background loop. Starts the session, decodes video into Frames,
extends the session before it expires, and stops it at Google when closed.
"""

import asyncio
import re
from collections.abc import Awaitable, Callable, Coroutine
from contextlib import suppress
from datetime import UTC, datetime
from typing import Any, cast

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.mediastreams import MediaStreamError, MediaStreamTrack
from av import AudioFrame, VideoFrame

from googlenestcam.audio_chunk import AudioChunk, Samples
from googlenestcam.errors import CameraOffError, GoogleApiError, StreamError
from googlenestcam.frame import Frame, Image
from googlenestcam.frame_size import Size, target_size
from googlenestcam.webrtc_offer import create_peer_connection, fix_google_answer

type RunCommand = Callable[[str, dict[str, Any]], Awaitable[dict[str, Any]]]

COMMAND = "sdm.devices.commands.CameraLiveStream."
EXTEND_EARLY_SECONDS = 60
CAMERA_OFF_MESSAGE = "not available for streaming"


def refused_error(error: GoogleApiError) -> StreamError:
    """Turn Google's refusal to start a Stream into a clear error."""
    if CAMERA_OFF_MESSAGE in str(error):
        return CameraOffError(
            "The Camera is turned off or offline. Turn it on in the Google Home"
            f" app, then try again. ({error})"
        )
    return StreamError(f"Google refused to start the Stream: {error}")


def parse_google_time(value: str) -> datetime:
    """Parse Google's RFC 3339 time, which may have more than 6 decimals."""
    value = re.sub(r"(\.\d{6})\d+", r"\1", value)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _rgb(frame: VideoFrame, size: Size | None) -> Image:
    if size is None:
        return cast(Image, frame.to_ndarray(format="rgb24"))
    width, height = target_size(size, frame.width, frame.height)
    return cast(Image, frame.to_ndarray(width=width, height=height, format="rgb24"))


def _samples(frame: AudioFrame) -> Samples:
    """Return the sound as samples x channels; aiortc decodes Opus to int16."""
    array = frame.to_ndarray()
    if frame.format.is_planar:
        array = array.T
    else:
        array = array.reshape(-1, len(frame.layout.channels))
    return cast(Samples, array.astype("int16", copy=False))


class WebRtcSession:
    """A live WebRTC session that hands each Frame and Audio chunk to callbacks."""

    def __init__(
        self,
        run_command: RunCommand,
        on_frame: Callable[[Frame], None],
        on_error: Callable[[Exception], None],
        size: Size | None = None,
        on_audio: Callable[[AudioChunk], None] | None = None,
    ) -> None:
        """Prepare a session.

        Args:
            run_command: Runs a ``CameraLiveStream`` command for this Camera.
            on_frame: Called with each new Frame.
            on_error: Called once the session stops working.
            size: Resize each Frame to this height or ``(width, height)``;
                ``None`` keeps it.
            on_audio: Called with each Audio chunk; ``None`` throws Audio away.
        """
        self._run_command = run_command
        self._on_frame = on_frame
        self._on_audio = on_audio
        self._on_error = on_error
        self._size = size
        self._connection: RTCPeerConnection | None = None
        self._media_session_id: str | None = None
        self._expires_at = datetime.now(UTC)
        self._tasks: set[asyncio.Task[None]] = set()
        self._closed = False

    async def start(self) -> None:
        """Ask Google for a session and connect to it.

        Raises:
            CameraOffError: If the Camera is turned off or offline.
            StreamError: If Google refuses or the answer cannot be used.
        """
        self._connection, offer = await create_peer_connection()
        self._connection.on("track", self._on_track)
        self._connection.on("connectionstatechange", self._on_state_change)
        try:
            results = await self._command("GenerateWebRtcStream", offerSdp=offer)
            self._keep_session(results)
            answer = fix_google_answer(results["answerSdp"])
            await self._connection.setRemoteDescription(
                RTCSessionDescription(sdp=answer, type="answer")
            )
        except GoogleApiError as error:
            await self.close()
            raise refused_error(error) from error
        except BaseException:
            await self.close()
            raise
        self._start_task(self._extend_until_closed())

    async def close(self) -> None:
        """Stop the tasks, stop the session at Google, then close the peer."""
        if self._closed:
            return
        self._closed = True
        for task in self._tasks:
            task.cancel()
        for task in list(self._tasks):
            with suppress(asyncio.CancelledError):
                await task
        if self._media_session_id:
            with suppress(Exception):
                await self._command(
                    "StopWebRtcStream", mediaSessionId=self._media_session_id
                )
        if self._connection is not None:
            await self._connection.close()

    async def _command(self, name: str, **params: Any) -> dict[str, Any]:
        return await self._run_command(COMMAND + name, params)

    def _keep_session(self, results: dict[str, Any]) -> None:
        self._media_session_id = results["mediaSessionId"]
        self._expires_at = parse_google_time(results["expiresAt"])

    def _start_task(self, coroutine: Coroutine[Any, Any, None]) -> None:
        task = asyncio.create_task(coroutine)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    def _fail(self, error: StreamError) -> None:
        if not self._closed:
            self._on_error(error)

    def _on_track(self, track: MediaStreamTrack) -> None:
        if track.kind == "video":
            self._start_task(self._read_video(track))
        elif self._on_audio is not None:
            self._start_task(self._read_audio(track, self._on_audio))
        else:
            self._start_task(self._discard(track))

    async def _on_state_change(self) -> None:
        if self._connection and self._connection.connectionState == "failed":
            self._fail(StreamError("The WebRTC connection to the Camera failed"))

    async def _read_video(self, track: MediaStreamTrack) -> None:
        try:
            while True:
                frame = await track.recv()
                received = datetime.now(UTC)
                if not isinstance(frame, VideoFrame):
                    continue
                image = await asyncio.to_thread(_rgb, frame, self._size)
                self._on_frame(Frame(image, received))
        except MediaStreamError:
            self._fail(StreamError("The Camera stopped sending video"))
        except Exception as error:
            self._fail(StreamError(f"Could not decode the video: {error}"))

    async def _read_audio(
        self, track: MediaStreamTrack, on_audio: Callable[[AudioChunk], None]
    ) -> None:
        with suppress(MediaStreamError):
            while True:
                frame = await track.recv()
                received = datetime.now(UTC)
                if isinstance(frame, AudioFrame):
                    on_audio(AudioChunk(_samples(frame), received))

    async def _discard(self, track: MediaStreamTrack) -> None:
        with suppress(MediaStreamError):
            while True:
                await track.recv()

    async def _extend_until_closed(self) -> None:
        try:
            while self._media_session_id:
                left = (self._expires_at - datetime.now(UTC)).total_seconds()
                await asyncio.sleep(max(1, left - EXTEND_EARLY_SECONDS))
                results = await self._command(
                    "ExtendWebRtcStream", mediaSessionId=self._media_session_id
                )
                self._keep_session(results)
        except GoogleApiError as error:
            self._fail(StreamError(f"Could not extend the Stream: {error}"))
