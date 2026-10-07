"""Hold Frames between the Stream and the reader (Latest and Every-frame mode)."""

import logging
import threading
from collections import deque
from typing import Literal, Self

from googlenestcam.errors import StreamError
from googlenestcam.frame import Frame

type OnFull = Literal["raise", "drop_oldest"]

logger = logging.getLogger(__name__)


class FrameBuffer:
    """A bounded ``deque`` of Frames, readable from any thread."""

    def __init__(
        self, size: int = 100, on_full: OnFull = "raise", *, log_drops: bool = True
    ) -> None:
        """Start empty.

        Args:
            size: The most unread Frames kept.
            on_full: ``"raise"`` makes the next read raise ``StreamError``;
                ``"drop_oldest"`` drops the oldest Frame.
            log_drops: Log and count drops in ``dropped``.
        """
        if size < 1:
            raise ValueError("queue_size must be at least 1")
        if on_full not in ("raise", "drop_oldest"):
            raise ValueError('on_full must be "raise" or "drop_oldest"')
        self._on_full = on_full
        self._log_drops = log_drops
        self._frames: deque[Frame] = deque(maxlen=size)
        self._dropped = 0
        self._error: Exception | None = None
        self._closed = False
        self._changed = threading.Condition()

    @classmethod
    def latest(cls) -> Self:
        """A one-Frame buffer where each new Frame quietly replaces the old one."""
        return cls(1, "drop_oldest", log_drops=False)

    @property
    def dropped(self) -> int:
        """How many Frames were dropped because the buffer was full."""
        return self._dropped

    def put(self, frame: Frame) -> None:
        """Add ``frame``, handling a full buffer as set by ``on_full``."""
        with self._changed:
            if len(self._frames) == self._frames.maxlen:
                self._handle_full()
            if self._error is None:
                self._frames.append(frame)  # deque drops the oldest when full
            self._changed.notify_all()

    def _handle_full(self) -> None:
        """Fail the reader for ``"raise"``; otherwise log the coming drop."""
        if self._on_full == "raise":
            self._error = StreamError(
                f"The Frame queue is full ({self._frames.maxlen} Frames); "
                "your code is reading too slowly. Set a bigger "
                'queue_size, or on_full="drop_oldest".'
            )
            return
        if not self._log_drops:
            return
        self._dropped += 1
        level = logging.WARNING if self._dropped == 1 else logging.DEBUG
        logger.log(
            level,
            "Frame dropped because your code reads too slowly "
            "(%d so far; see stream.dropped)",
            self._dropped,
        )

    def fail(self, error: Exception) -> None:
        """Make the next read raise ``error``."""
        with self._changed:
            self._error = error
            self._changed.notify_all()

    def close(self) -> None:
        """End all reads."""
        with self._changed:
            self._closed = True
            self._changed.notify_all()

    def get(self) -> Frame | None:
        """Wait for the oldest unread Frame.

        Returns:
            The oldest unread Frame, or ``None`` once closed.

        Raises:
            Exception: The error passed to ``fail``, or ``StreamError`` when
                the buffer filled up.
        """
        with self._changed:
            self._changed.wait_for(
                lambda: self._frames or self._closed or self._error is not None
            )
            if self._error is not None:
                raise self._error
            if self._closed:
                return None
            return self._frames.popleft()
