"""Smoke test that the package imports."""

import googlenestcam


def test_package_imports() -> None:
    """The package can be imported."""
    assert googlenestcam.__doc__


def test_stream_names_are_exported() -> None:
    """Stream types, Frame and StreamError are on the package."""
    for name in (
        "Frame",
        "Stream",
        "AsyncStream",
        "StreamError",
        "CameraOffError",
        "AudioChunk",
    ):
        assert hasattr(googlenestcam, name)
