"""The developer's Nest account: lists and picks Cameras."""

from typing import Any, Literal

import httpx

from googlenestcam import background_loop, sdm
from googlenestcam.auth import GoogleAuth
from googlenestcam.camera import Camera
from googlenestcam.credentials import Credentials, load_credentials
from googlenestcam.find_camera import find_camera
from googlenestcam.token_store import TokenPath


class Nest:
    """Access to the Cameras on one Google account.

    Most code uses ``googlenestcam.list_cameras()`` and
    ``googlenestcam.camera()``, which share one default ``Nest``. Make your own
    to pass settings in code.
    """

    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        project_id: str | None = None,
        credentials: Credentials | None = None,
        token_path: TokenPath | None = None,
        on_missing_token: Literal["login", "raise"] = "login",
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Set up access; see ``load_credentials`` and ``find_token_path``.

        Args:
            client_id: OAuth client ID.
            client_secret: OAuth client secret.
            project_id: Device Access project ID.
            credentials: Ready-made Credentials, instead of the three values.
            token_path: Where the Token is kept.
            on_missing_token: ``"login"`` or ``"raise"`` when there is no Token.
            transport: Custom ``httpx`` transport (for tests and proxies).
        """
        self.credentials = credentials or load_credentials(
            client_id, client_secret, project_id
        )
        self.token_path = token_path
        self._auth = GoogleAuth(
            self.credentials, token_path=token_path, on_missing_token=on_missing_token
        )
        self._transport = transport
        self._client: httpx.AsyncClient | None = None

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=20, transport=self._transport)
        return self._client

    async def _access_token(self) -> str:
        return await self._auth.access_token(await self._http())

    async def _list_cameras(self) -> list[Camera]:
        devices = await sdm.list_devices(
            await self._http(), await self._access_token(), self.credentials.project_id
        )
        cameras = (Camera.from_device(device, self) for device in devices)
        return [camera for camera in cameras if camera is not None]

    async def _execute_command(
        self, device_id: str, command: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Run a device command on the background loop; see ``sdm.execute_command``."""
        return await sdm.execute_command(
            await self._http(), await self._access_token(), device_id, command, params
        )

    async def _camera(self, name_or_id: str) -> Camera:
        return find_camera(await self._list_cameras(), name_or_id)

    def list_cameras(self) -> list[Camera]:
        """Return every Camera on the account that streams over WebRTC."""
        return background_loop.run(self._list_cameras())

    async def list_cameras_async(self) -> list[Camera]:
        """Async version of ``list_cameras``."""
        return await background_loop.run_async(self._list_cameras())

    def camera(self, name_or_id: str) -> Camera:
        """Return one Camera by its Google Home name (any case) or Google ID.

        Raises:
            CameraNotFoundError: If none match, or several share the name.
        """
        return background_loop.run(self._camera(name_or_id))

    async def camera_async(self, name_or_id: str) -> Camera:
        """Async version of ``camera``."""
        return await background_loop.run_async(self._camera(name_or_id))
