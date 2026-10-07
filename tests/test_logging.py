"""Tests that the package's logging stays under the developer's control."""

import logging

import googlenestcam  # noqa: F401  (importing sets up the logger)


def test_package_logger_has_only_a_null_handler() -> None:
    """The package adds no output of its own; the developer's config decides."""
    handlers = logging.getLogger("googlenestcam").handlers
    assert [type(h) for h in handlers] == [logging.NullHandler]
