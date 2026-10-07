"""A fake Google for Stream tests.

Answers the token, device list and WebRTC commands like Google. For
``GenerateWebRtcStream`` it starts a local aiortc peer that sends made-up
video and silence over this machine, and answers with a blank ICE candidate
foundation as Google does.
"""

import json
import re
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import numpy as np
from aiortc import (
    RTCConfiguration,
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
)
from aiortc.mediastreams import AudioStreamTrack
from av import VideoFrame

from tests.fakes import device

COMMAND_PREFIX = "sdm.devices.commands.CameraLiveStream."
WIDTH, HEIGHT = 64, 48
COLOUR = (200, 30, 30)


class FakeVideo(VideoStreamTrack):
    """Sends a plain red picture at 30 Frames a second."""

    async def recv(self) -> VideoFrame:
        """Return the next picture."""
        pts, time_base = await self.next_timestamp()
        image = np.full((HEIGHT, WIDTH, 3), COLOUR, dtype=np.uint8)
        frame = VideoFrame.from_ndarray(image, format="rgb24")
        frame.pts, frame.time_base = pts, time_base
        return frame


class FakeGoogle:
    """Fake Google with a request log.

    Attributes:
        commands: Every device command as ``(short name, params)``.
        expires_in: Seconds until each media session expires.
        refuse_stream: When set, ``GenerateWebRtcStream`` fails with this message.
    """

    def __init__(self) -> None:
        """Start with one Camera named "Front door"."""
        self.devices = [device("cam1", room="Front door")]
        self.commands: list[tuple[str, dict[str, Any]]] = []
        self.expires_in = 300
        self.refuse_stream: str | None = None
        self.peers: list[RTCPeerConnection] = []
        self.transport = httpx.MockTransport(self._handle)
        self._sessions = 0

    def command_names(self) -> list[str]:
        """Short names of the commands seen so far, in order."""
        return [name for name, _ in self.commands]

    async def close(self) -> None:
        """Close every fake peer."""
        for peer in self.peers:
            await peer.close()

    async def _handle(self, request: httpx.Request) -> httpx.Response:
        if request.url.host == "oauth2.googleapis.com":
            return httpx.Response(200, json={"access_token": "a", "expires_in": 3600})
        if request.url.path.endswith(":executeCommand"):
            body = json.loads(request.content)
            return await self._command(body["command"], body["params"])
        return httpx.Response(200, json={"devices": self.devices})

    async def _command(self, command: str, params: dict[str, Any]) -> httpx.Response:
        name = command.removeprefix(COMMAND_PREFIX)
        self.commands.append((name, params))
        if name == "GenerateWebRtcStream":
            if self.refuse_stream:
                error = {"error": {"message": self.refuse_stream}}
                return httpx.Response(400, json=error)
            answer = await self._answer(params["offerSdp"])
            return httpx.Response(200, json={"results": self._session(answer)})
        if name == "ExtendWebRtcStream":
            return httpx.Response(200, json={"results": self._session()})
        return httpx.Response(200, json={})

    def _session(self, answer: str | None = None) -> dict[str, str]:
        self._sessions += 1
        expires = datetime.now(UTC) + timedelta(seconds=self.expires_in)
        results = {
            "mediaSessionId": f"session-{self._sessions}",
            "expiresAt": expires.isoformat().replace("+00:00", "Z"),
        }
        if answer is not None:
            results["answerSdp"] = answer
        return results

    async def _answer(self, offer: str) -> str:
        peer = RTCPeerConnection(RTCConfiguration(iceServers=[]))
        self.peers.append(peer)
        await peer.setRemoteDescription(RTCSessionDescription(offer, "offer"))
        for transceiver in peer.getTransceivers():
            if transceiver.kind == "audio":
                transceiver.sender.replaceTrack(AudioStreamTrack())
            else:
                transceiver.sender.replaceTrack(FakeVideo())
            transceiver.direction = "sendonly"
        await peer.setLocalDescription(await peer.createAnswer())
        # Google sends a blank candidate foundation that aiortc can't parse.
        return re.sub(r"a=candidate:\S+ ", "a=candidate: ", peer.localDescription.sdp)
