"""Tests for small helpers of the WebRTC session."""

from datetime import UTC, datetime

from googlenestcam.webrtc_session import parse_google_time


def test_google_time_with_nanoseconds_is_parsed() -> None:
    """Google sends nine decimals and a ``Z``; extra decimals are cut off."""
    parsed = parse_google_time("2026-10-08T01:02:03.123456789Z")
    assert parsed == datetime(2026, 10, 8, 1, 2, 3, 123456, tzinfo=UTC)


def test_google_time_without_decimals_is_parsed() -> None:
    """A whole-second time is parsed too."""
    parsed = parse_google_time("2026-10-08T01:02:03Z")
    assert parsed == datetime(2026, 10, 8, 1, 2, 3, tzinfo=UTC)
