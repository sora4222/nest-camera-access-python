"""Keep the last few seconds of unread Audio."""

import threading
from collections import deque

from googlenestcam.audio_chunk import CHUNK_SECONDS, AudioChunk


class AudioBuffer:
    """A bounded queue of Audio chunks that drops the oldest when full."""

    def __init__(self, seconds: float = 5) -> None:
        """Start empty, keeping at most ``seconds`` of unread Audio."""
        self._chunks: deque[AudioChunk] = deque(
            maxlen=max(1, round(seconds / CHUNK_SECONDS))
        )
        self._error: Exception | None = None
        self._closed = False
        self._changed = threading.Condition()

    def put(self, chunk: AudioChunk) -> None:
        """Add ``chunk``, dropping the oldest if the buffer is full."""
        with self._changed:
            self._chunks.append(chunk)
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

    def get(self) -> AudioChunk | None:
        """Wait for the next chunk in order.

        Returns:
            The oldest unread chunk, or ``None`` once closed.

        Raises:
            Exception: The error passed to ``fail``.
        """
        with self._changed:
            self._changed.wait_for(
                lambda: self._chunks or self._closed or self._error is not None
            )
            if self._error is not None:
                raise self._error
            if self._closed:
                return None
            return self._chunks.popleft()
