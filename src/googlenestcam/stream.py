"""A live Stream of Frames from one Camera."""

import asyncio
from collections.abc import AsyncIterator, Iterator
from types import TracebackType
from typing import Literal, Self

from googlenestcam import background_loop
from googlenestcam.frame import Frame
from googlenestcam.frame_size import Size
from googlenestcam.frame_queue import FrameQueue, OnFull
from googlenestcam.latest_frame import LatestFrame
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
    ) -> None:
        if frames == "latest":
            self._frames: LatestFrame | FrameQueue = LatestFrame()
        elif frames == "all":
            self._frames = FrameQueue(queue_size, on_full)
        else:
            raise ValueError('frames must be "latest" or "all"')
        self._session = ReconnectingSession(
            run_command, self._frames.put, self._frames.fail, retries, size
        )

    @property
    def dropped(self) -> int:
        """Frames dropped in Every-frame mode with ``on_full="drop_oldest"``."""
        return self._frames.dropped if isinstance(self._frames, FrameQueue) else 0


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
        """Stop the Stream at Google and end ``frames()``."""
        self._frames.close()
        background_loop.run(self._session.close())

    def frames(self) -> Iterator[Frame]:
        """Yield Frames: the newest in Latest mode, all in order in Every-frame mode.

        Raises:
            StreamError: If the Stream stops working.
        """
        while (frame := self._frames.get()) is not None:
            yield frame


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
        """Stop the Stream at Google and end ``frames()``."""
        self._frames.close()
        await background_loop.run_async(self._session.close())

    async def frames(self) -> AsyncIterator[Frame]:
        """Yield Frames: the newest in Latest mode, all in order in Every-frame mode.

        Raises:
            StreamError: If the Stream stops working.
        """
        while (frame := await asyncio.to_thread(self._frames.get)) is not None:
            yield frame
