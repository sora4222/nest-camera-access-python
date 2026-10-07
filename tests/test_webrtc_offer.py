"""Tests for the SDP offer Google accepts and the fix for Google's answer."""

import pytest

from googlenestcam.webrtc_offer import (
    create_peer_connection,
    fix_google_answer,
    validate_offer,
)


async def test_offer_follows_nest_rules() -> None:
    """Audio, video, then a data channel; receive-only Opus and H.264."""
    connection, offer = await create_peer_connection()
    await connection.close()
    media = [line.split(" ", 1)[0] for line in offer.splitlines() if line[:2] == "m="]
    audio = offer.split("m=audio", 1)[1].split("m=video", 1)[0]
    video = offer.split("m=video", 1)[1].split("m=application", 1)[0]
    assert media == ["m=audio", "m=video", "m=application"]
    assert "a=recvonly" in audio
    assert " opus/48000/2" in audio.lower()
    assert " H264/90000" in video
    assert "profile-level-id=42e01f" in video
    assert offer.endswith("\n")


def test_wrong_media_order_is_refused() -> None:
    """An offer with video before audio is refused."""
    offer = (
        "v=0\r\n"
        "m=video 9 UDP/TLS/RTP/SAVPF 96\r\n"
        "m=audio 9 UDP/TLS/RTP/SAVPF 111\r\n"
        "a=recvonly\r\n"
        "a=rtpmap:111 opus/48000/2\r\n"
        "m=application 9 UDP/DTLS/SCTP webrtc-datachannel\r\n"
    )
    with pytest.raises(RuntimeError, match="order"):
        validate_offer(offer)


def test_offer_gets_a_trailing_newline() -> None:
    """Google needs the offer to end with a newline."""
    offer = (
        "v=0\r\nm=audio 9 X 111\r\na=recvonly\r\na=rtpmap:111 opus/48000/2\r\n"
        "m=video 9 X 96\r\nm=application 9 X webrtc-datachannel"
    )
    assert validate_offer(offer).endswith("\r\n")


def test_blank_candidate_foundation_is_named() -> None:
    """Google's blank candidate foundation is replaced so aiortc can read it."""
    answer = "v=0\r\na=candidate: 1 udp 2113932031 74.125.1.1 19305 typ host\r\n"
    fixed = fix_google_answer(answer)
    assert "a=candidate:google 1 udp" in fixed
    assert fixed.endswith("\r\n")
