"""Quick access to Google Nest Cameras for Python developers."""

from googlenestcam.camera import Camera
from googlenestcam.credentials import Credentials, load_credentials
from googlenestcam.default_nest import (
    camera,
    camera_async,
    list_cameras,
    list_cameras_async,
)
from googlenestcam.errors import (
    CameraNotFoundError,
    CredentialsError,
    GoogleNestCamError,
    LoginError,
    MissingExtraError,
    MissingTokenError,
    GoogleApiError,
    OnePasswordError,
    SnapshotTimeoutError,
    StreamError,
    TokenError,
)
from googlenestcam.frame import Frame
from googlenestcam.login import login
from googlenestcam.nest import Nest
from googlenestcam.stream import AsyncStream, Stream

__all__ = [
    "AsyncStream",
    "Camera",
    "CameraNotFoundError",
    "Credentials",
    "CredentialsError",
    "Frame",
    "GoogleApiError",
    "GoogleNestCamError",
    "LoginError",
    "MissingExtraError",
    "MissingTokenError",
    "Nest",
    "OnePasswordError",
    "SnapshotTimeoutError",
    "Stream",
    "StreamError",
    "TokenError",
    "camera",
    "camera_async",
    "list_cameras",
    "list_cameras_async",
    "load_credentials",
    "login",
]
