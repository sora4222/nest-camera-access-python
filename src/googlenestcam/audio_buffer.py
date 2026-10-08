"""Keep the last few seconds of unread Audio."""

from googlenestcam.audio_chunk import CHUNK_SECONDS, AudioChunk
from googlenestcam.media_buffer import MediaBuffer


class AudioBuffer(MediaBuffer[AudioChunk]):
    """A bounded queue of Audio chunks that drops the oldest when full."""

    def __init__(self, seconds: float = 5) -> None:
        """Start empty, keeping at most ``seconds`` of unread Audio."""
        super().__init__(max(1, round(seconds / CHUNK_SECONDS)))
