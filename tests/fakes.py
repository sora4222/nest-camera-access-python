"""Fake Google replies shared by tests."""

from typing import Any


def device(
    device_id: str = "cam1",
    *,
    custom_name: str = "",
    room: str = "Front door",
    kind: str = "CAMERA",
    protocols: tuple[str, ...] = ("WEB_RTC",),
) -> dict[str, Any]:
    """Return one SDM device as Google sends it."""
    return {
        "name": f"enterprises/project/devices/{device_id}",
        "type": f"sdm.devices.types.{kind}",
        "traits": {
            "sdm.devices.traits.Info": {"customName": custom_name},
            "sdm.devices.traits.CameraLiveStream": {
                "supportedProtocols": list(protocols)
            },
        },
        "parentRelations": [
            {
                "parent": "enterprises/project/structures/s/rooms/r",
                "displayName": room,
            }
        ],
    }
