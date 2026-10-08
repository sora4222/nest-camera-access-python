"""Hold Frames between the Stream and the reader (Latest and Every-frame mode)."""

import logging
from typing import Literal, Self

from googlenestcam.errors import StreamError
from googlenestcam.frame import Frame
from googlenestcam.media_buffer import MediaBuffer

type OnFull = Literal["raise", "drop_oldest"]

logger = logging.getLogger(__name__)


class FrameBuffer(MediaBuffer[Frame]):
    """A bounded buffer of Frames that raises or drops when full."""

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
        if on_full not in ("raise", "drop_oldest"):
            raise ValueError('on_full must be "raise" or "drop_oldest"')
        super().__init__(size)
        self._on_full_action = on_full
        self._log_drops = log_drops
        self._dropped = 0

    @classmethod
    def latest(cls) -> Self:
        """A one-Frame buffer where each new Frame quietly replaces the old one."""
        return cls(1, "drop_oldest", log_drops=False)

    @property
    def dropped(self) -> int:
        """How many Frames were dropped because the buffer was full."""
        return self._dropped

    def _on_full(self) -> None:
        """Fail the reader for ``"raise"``; otherwise log the coming drop."""
        if self._on_full_action == "raise":
            self._error = StreamError(
                f"The Frame queue is full ({self._items.maxlen} Frames); "
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
