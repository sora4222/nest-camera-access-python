"""Keep a live WebRTC session going, starting a new one after a drop."""

import asyncio
from collections.abc import Callable
from contextlib import suppress

from googlenestcam.audio_chunk import AudioChunk
from googlenestcam.errors import CameraOffError, StreamError
from googlenestcam.frame import Frame
from googlenestcam.frame_size import Size
from googlenestcam.webrtc_session import RunCommand, WebRtcSession

RETRY_DELAY_SECONDS = 1.0


class ReconnectingSession:
    """A WebRTC session that reconnects by itself after a drop.

    Tries up to ``retries`` times in a row. The count resets once a Frame
    arrives on a new session. After the last failed try, ``on_error`` is
    called.
    """

    def __init__(
        self,
        run_command: RunCommand,
        on_frame: Callable[[Frame], None],
        on_error: Callable[[Exception], None],
        retries: int = 3,
        size: Size | None = None,
        on_audio: Callable[[AudioChunk], None] | None = None,
    ) -> None:
        """Prepare the session; see ``WebRtcSession`` for the arguments."""
        if retries < 0:
            raise ValueError("retries must be 0 or more")
        self._run_command = run_command
        self._on_frame = on_frame
        self._on_error = on_error
        self._retries = retries
        self._size = size
        self._on_audio = on_audio
        self._failures = 0
        self._session: WebRtcSession | None = None
        self._reconnecting: asyncio.Task[None] | None = None
        self._closed = False

    async def start(self) -> None:
        """Start the first session.

        Raises:
            StreamError: If Google refuses it.
        """
        self._session = self._new_session()
        await self._session.start()

    async def close(self) -> None:
        """Stop reconnecting and close the current session."""
        self._closed = True
        if self._reconnecting is not None:
            self._reconnecting.cancel()
            with suppress(asyncio.CancelledError):
                await self._reconnecting
        if self._session is not None:
            await self._session.close()

    def _new_session(self) -> WebRtcSession:
        session: WebRtcSession

        def on_frame(frame: Frame) -> None:
            self._failures = 0
            self._on_frame(frame)

        def on_error(error: Exception) -> None:
            if session is self._session:
                self._dropped(error)

        session = WebRtcSession(
            self._run_command, on_frame, on_error, self._size, self._on_audio
        )
        return session

    def _dropped(self, error: Exception) -> None:
        if self._closed or self._reconnecting is not None:
            return
        self._reconnecting = asyncio.create_task(self._reconnect(error))

    async def _reconnect(self, error: Exception) -> None:
        try:
            if self._session is not None:
                await self._session.close()
            while self._failures < self._retries:
                self._failures += 1
                await asyncio.sleep(RETRY_DELAY_SECONDS)
                session = self._new_session()
                self._session = session
                try:
                    await session.start()
                    return
                except StreamError as new_error:
                    error = new_error
            self._on_error(self._gave_up(error))
        finally:
            self._reconnecting = None

    def _gave_up(self, error: Exception) -> Exception:
        if not self._retries:
            return error
        kind = CameraOffError if isinstance(error, CameraOffError) else StreamError
        return kind(f"Gave up reconnecting after {self._retries} tries: {error}")
