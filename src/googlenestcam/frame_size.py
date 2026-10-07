"""The width and height Frames are resized to (Frame size)."""

from typing import Any

type Size = tuple[int, int]


def check_size(size: Any) -> Size | None:
    """Return ``size`` as ``(width, height)``, or ``None`` for the Camera's size.

    Raises:
        ValueError: If ``size`` is not two whole numbers of at least 1.
    """
    if size is None:
        return None
    if (
        isinstance(size, tuple | list)
        and len(size) == 2
        and all(type(side) is int and side >= 1 for side in size)
    ):
        return (size[0], size[1])
    raise ValueError(f"size must be (width, height) in whole pixels, not {size!r}")
