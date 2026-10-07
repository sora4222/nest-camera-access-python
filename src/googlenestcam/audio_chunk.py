"""A short run of sound from a Camera."""

from dataclasses import dataclass
from datetime import datetime

import numpy as np
import numpy.typing as npt

SAMPLE_RATE = 48_000
CHUNK_SECONDS = 0.02

type Samples = npt.NDArray[np.int16]


@dataclass(frozen=True, eq=False)
class AudioChunk:
    """A short run of Audio from a Stream.

    Attributes:
        samples: The sound as a NumPy int16 array, samples x channels.
        time: When the chunk was received, on the same clock as ``Frame.time``.
        sample_rate: Samples per second (48,000).
    """

    samples: Samples
    time: datetime
    sample_rate: int = SAMPLE_RATE
