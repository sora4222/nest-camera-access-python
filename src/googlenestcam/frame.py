"""One picture from a Camera."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np
import numpy.typing as npt

type Image = npt.NDArray[np.uint8]


@dataclass(frozen=True, eq=False)
class Frame:
    """One picture from a Stream.

    Attributes:
        image: The picture as a NumPy array, height x width x 3, RGB, uint8.
        time: When the Frame was received, as a UTC datetime.
    """

    image: Image
    time: datetime

    def __array__(self, dtype: Any = None, copy: bool | None = None) -> np.ndarray:
        """Let ``np.asarray(frame)`` return the picture."""
        if dtype is None and not copy:
            return self.image
        return np.array(self.image, dtype=dtype, copy=copy)
