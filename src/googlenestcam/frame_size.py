"""The width and height Frames are resized to (Frame size)."""

from typing import Any

type Size = int | tuple[int, int]


def _is_pixels(value: Any) -> bool:
    return type(value) is int and value >= 1


def check_size(size: Any) -> Size | None:
    """Return ``size`` as a height or ``(width, height)``; ``None`` keeps the size.

    Raises:
        ValueError: If ``size`` is not a whole number, or two, of at least 1.
    """
    if size is None:
        return None
    if _is_pixels(size):
        return size
    if isinstance(size, tuple | list) and len(size) == 2 and all(map(_is_pixels, size)):
        return (size[0], size[1])
    raise ValueError(
        f"size must be a height like 720, or (width, height), not {size!r}"
    )


def target_size(size: Size, width: int, height: int) -> tuple[int, int]:
    """Return the ``(width, height)`` to resize a ``width`` x ``height`` picture to.

    A single number is the new height; the width keeps the picture's shape.
    """
    if isinstance(size, int):
        return max(1, round(width * size / height)), size
    return size
