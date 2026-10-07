"""Smoke test that the package imports."""

import googlenestcam


def test_package_imports() -> None:
    """The package can be imported."""
    assert googlenestcam.__doc__
