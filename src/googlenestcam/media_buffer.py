"""Hold Frames or Audio chunks between the Stream and the reader."""

import threading
from collections import deque


class MediaBuffer[T]:
    """A bounded ``deque`` readable from any thread.

    When full, the oldest unread item is dropped. Subclasses can change that
    by overriding ``_on_full``.
    """

    def __init__(self, size: int) -> None:
        """Start empty, keeping at most ``size`` unread items.

        Raises:
            ValueError: If ``size`` is less than 1.
        """
        if size < 1:
            raise ValueError("queue_size must be at least 1")
        self._items: deque[T] = deque(maxlen=size)
        self._error: Exception | None = None
        self._closed = False
        self._changed = threading.Condition()

    def put(self, item: T) -> None:
        """Add ``item``; when full, ``_on_full`` runs first."""
        with self._changed:
            if len(self._items) == self._items.maxlen:
                self._on_full()
            if self._error is None:
                self._items.append(item)  # deque drops the oldest when full
            self._changed.notify_all()

    def _on_full(self) -> None:
        """Run under the lock before a put into a full buffer."""

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

    def get(self) -> T | None:
        """Wait for the oldest unread item.

        Returns:
            The oldest unread item, or ``None`` once closed.

        Raises:
            Exception: The error passed to ``fail``, or one set by ``_on_full``.
        """
        with self._changed:
            self._changed.wait_for(
                lambda: self._items or self._closed or self._error is not None
            )
            if self._error is not None:
                raise self._error
            if self._closed:
                return None
            return self._items.popleft()
