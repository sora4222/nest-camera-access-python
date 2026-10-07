"""Keep only the newest Frame (Latest mode)."""

import threading

from googlenestcam.frame import Frame


class LatestFrame:
    """One slot that each new Frame replaces, readable from any thread."""

    def __init__(self) -> None:
        """Start empty."""
        self._frame: Frame | None = None
        self._unread = False
        self._error: Exception | None = None
        self._closed = False
        self._changed = threading.Condition()

    def put(self, frame: Frame) -> None:
        """Replace the slot with ``frame``."""
        with self._changed:
            self._frame = frame
            self._unread = True
            self._changed.notify_all()

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
        """Wait for a Frame newer than the last one read.

        Returns:
            The newest Frame, or ``None`` once closed.

        Raises:
            Exception: The error passed to ``fail``.
        """
        with self._changed:
            self._changed.wait_for(
                lambda: self._unread or self._closed or self._error is not None
            )
            if self._error is not None:
                raise self._error
            if self._closed:
                return None
            self._unread = False
            return self._frame
