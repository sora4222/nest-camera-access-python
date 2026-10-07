"""Turn a Frame's picture into a Pillow image or JPEG bytes.

Pillow comes from the ``googlenestcam[images]`` extra and is imported only here,
inside the functions, so ``import googlenestcam`` works without it.
"""

import io
from types import ModuleType
from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from googlenestcam.errors import MissingExtraError

if TYPE_CHECKING:
    from PIL.Image import Image as PilImage


def _pillow() -> ModuleType:
    """Import ``PIL.Image``, or say which extra to install."""
    try:
        from PIL import Image
    except ImportError as error:
        raise MissingExtraError(
            "Pillow is needed for this; install googlenestcam[images]"
        ) from error
    return Image


def to_pil(image: npt.NDArray[np.uint8]) -> "PilImage":
    """Return an H x W x 3 RGB uint8 array as a Pillow RGB image."""
    return _pillow().fromarray(image)


def to_jpeg(image: npt.NDArray[np.uint8], quality: int = 85) -> bytes:
    """Return an H x W x 3 RGB uint8 array as JPEG bytes (quality 1 to 95)."""
    buffer = io.BytesIO()
    to_pil(image).save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()
