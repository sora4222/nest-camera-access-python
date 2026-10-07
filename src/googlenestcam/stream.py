"""A live Stream of Frames and Audio from one Camera."""

import asyncio
from collections.abc import AsyncIterator, Iterator
from types import TracebackType
from typing import Literal, Self

from googlenestcam import background_loop
from googlenestcam.audio_buffer import AudioBuffer
from googlenestcam.audio_chunk import AudioChunk
from googlenestcam.frame import Frame
from googlenestcam.frame_buffer import FrameBuffer, OnFull
from googlenestcam.frame_size import Size
from googlenestcam.reconnect import ReconnectingSession
from googlenestcam.webrtc_session import RunCommand

type FrameMode = Literal["latest", "all"]


class _StreamParts:
    def __init__(
        self,
        run_command: RunCommand,
        frames: FrameMode = "latest",
        queue_size: int = 100,
        on_full: OnFull = "raise",
        retries: int = 3,
        size: Size | None = None,
        audio: bool = True,
    ) -> None:
        if frames == "latest":
            self._frames = FrameBuffer.latest()
        elif frames == "all":
            self._frames = FrameBuffer(queue_size, on_full)
        else:
            raise ValueError('frames must be "latest" or "all"')
        self._audio = AudioBuffer() if audio else None
        self._session = ReconnectingSession(
            run_command,
            self._frames.put,
            self._fail,
            retries,
            size,
            self._audio.put if self._audio else None,
        )

    def _fail(self, error: Exception) -> None:
        self._frames.fail(error)
        if self._audio is not None:
            self._audio.fail(error)

    def _close_readers(self) -> None:
        self._frames.close()
        if self._audio is not None:
            self._audio.close()

    def _audio_buffer(self) -> AudioBuffer:
        if self._audio is None:
            raise ValueError("Audio is off for this Stream (audio=False)")
        return self._audio

    @property
    def dropped(self) -> int:
        """Frames dropped in Every-frame mode with ``on_full="drop_oldest"``."""
        return self._frames.dropped


class Stream(_StreamParts):
    """A live Stream. Use it in a ``with`` block.

    Leaving the block stops the Stream at Google, also after an error.
    """

    def __enter__(self) -> Self:
        """Start the Stream.

        Raises:
            StreamError: If Google refuses to start it.
        """
        background_loop.run(self._session.start())
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Stop the Stream at Google and end ``frames()`` and ``audio()``."""
        self._close_readers()
        background_loop.run(self._session.close())

    def frames(self) -> Iterator[Frame]:
        """Yield Frames: the newest in Latest mode, all in order in Every-frame mode.

        Raises:
            StreamError: If the Stream stops working.
        """
        while (frame := self._frames.get()) is not None:
            yield frame

    def audio(self) -> Iterator[AudioChunk]:
        """Yield Audio chunks in order. Can be read in another thread than ``frames()``.

        Only the last few seconds of unread Audio are kept.

        Raises:
            ValueError: If the Stream was opened with ``audio=False``.
            StreamError: If the Stream stops working.
        """
        buffer = self._audio_buffer()
        while (chunk := buffer.get()) is not None:
            yield chunk


class AsyncStream(_StreamParts):
    """Async version of ``Stream``. Use it in an ``async with`` block."""

    async def __aenter__(self) -> Self:
        """Start the Stream.

        Raises:
            StreamError: If Google refuses to start it.
        """
        await background_loop.run_async(self._session.start())
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Stop the Stream at Google and end ``frames()`` and ``audio()``."""
        self._close_readers()
        await background_loop.run_async(self._session.close())

    async def frames(self) -> AsyncIterator[Frame]:
        """Yield Frames: the newest in Latest mode, all in order in Every-frame mode.

        Raises:
            StreamError: If the Stream stops working.
        """
        while (frame := await asyncio.to_thread(self._frames.get)) is not None:
            yield frame

    async def audio(self) -> AsyncIterator[AudioChunk]:
        """Async version of ``Stream.audio``."""
        buffer = self._audio_buffer()
        while (chunk := await asyncio.to_thread(buffer.get)) is not None:
            yield chunk
