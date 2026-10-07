"""Build the SDP offer Google's Nest API accepts, and fix Google's answer."""

from aiortc import (
    RTCConfiguration,
    RTCPeerConnection,
    RTCRtpCodecCapability,
    RTCRtpSender,
)

NEST_H264_PROFILE = "42e01f"
MEDIA_ORDER = ["m=audio", "m=video", "m=application"]


def _codecs(kind: str, mime_type: str) -> list[RTCRtpCodecCapability]:
    capabilities = RTCRtpSender.getCapabilities(kind)
    return [c for c in capabilities.codecs if c.mimeType.lower() == mime_type]


def _nest_h264_codecs() -> list[RTCRtpCodecCapability]:
    return [
        codec
        for codec in _codecs("video", "video/h264")
        if codec.parameters.get("profile-level-id") == NEST_H264_PROFILE
    ]


def validate_offer(offer_sdp: str) -> str:
    """Check an offer meets Nest's rules and give it a trailing newline.

    Raises:
        RuntimeError: If the media order, audio direction or audio codec is
            wrong.
    """
    offer = offer_sdp if offer_sdp.endswith("\n") else offer_sdp + "\r\n"
    media = [line.split(" ", 1)[0] for line in offer.splitlines() if line[:2] == "m="]
    if media != MEDIA_ORDER:
        raise RuntimeError("Offer media must be in the order audio, video, application")
    audio = offer.split("m=audio", 1)[1].split("m=video", 1)[0]
    if "a=recvonly" not in audio:
        raise RuntimeError("Offer audio must be receive-only")
    if " opus/48000/" not in audio.lower():
        raise RuntimeError("Offer audio must use Opus")
    return offer


def fix_google_answer(answer_sdp: str) -> str:
    """Name Google's blank ICE candidate foundation so aiortc can parse it."""
    lines = [
        line.replace("a=candidate: ", "a=candidate:google ", 1)
        for line in answer_sdp.splitlines()
    ]
    return "\r\n".join(lines) + "\r\n"


async def create_peer_connection() -> tuple[RTCPeerConnection, str]:
    """Return a receive-only peer connection and its checked Nest offer.

    Raises:
        RuntimeError: If the offer breaks Nest's rules.
    """
    connection = RTCPeerConnection(RTCConfiguration(iceServers=[]))
    audio = connection.addTransceiver("audio", direction="recvonly")
    video = connection.addTransceiver("video", direction="recvonly")
    audio.setCodecPreferences(_codecs("audio", "audio/opus"))
    video.setCodecPreferences(_nest_h264_codecs())
    connection.createDataChannel("dataSendChannel")
    await connection.setLocalDescription(await connection.createOffer())
    return connection, validate_offer(connection.localDescription.sdp)
