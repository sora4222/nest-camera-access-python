"""A live Stream of Frames from one Camera."""

import asyncio
from collections.abc import AsyncIterator, Iterator
from types import TracebackType
from typing import Self

from googlenestcam import background_loop
from googlenestcam.frame import Frame
from googlenestcam.latest_frame import LatestFrame
from googlenestcam.webrtc_session import RunCommand, WebRtcSession


class _StreamParts:
    def __init__(self, run_command: RunCommand) -> None:
        self._frames = LatestFrame()
        self._session = WebRtcSession(
            run_command, on_frame=self._frames.put, on_error=self._frames.fail
        )


class Stream(_StreamParts):
    """A live Stream in Latest mode. Use it in a ``with`` block.

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
        """Yield the newest Frame each time; older unread Frames are skipped.

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
        """Yield the newest Frame each time; older unread Frames are skipped.

        Raises:
            StreamError: If the Stream stops working.
        """
        while (frame := await asyncio.to_thread(self._frames.get)) is not None:
            yield frame
