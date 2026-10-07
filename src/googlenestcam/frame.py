"""One picture from a Camera."""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

import numpy as np
import numpy.typing as npt

from googlenestcam import pillow_image

if TYPE_CHECKING:
    from PIL.Image import Image as PilImage

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

    def to_pil(self) -> "PilImage":
        """Return the picture as a Pillow RGB image. Needs ``googlenestcam[images]``."""
        return pillow_image.to_pil(self.image)

    def to_jpeg(self, quality: int = 85) -> bytes:
        """Return the picture as JPEG bytes. Needs ``googlenestcam[images]``.

        Args:
            quality: JPEG quality, 1 (smallest) to 95 (best).
        """
        return pillow_image.to_jpeg(self.image, quality=quality)
