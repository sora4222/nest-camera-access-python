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
    MissingTokenError,
    OnePasswordError,
    GoogleApiError,
    TokenError,
)
from googlenestcam.login import login
from googlenestcam.nest import Nest

__all__ = [
    "Camera",
    "CameraNotFoundError",
    "Credentials",
    "CredentialsError",
    "GoogleApiError",
    "GoogleNestCamError",
    "LoginError",
    "MissingTokenError",
    "Nest",
    "OnePasswordError",
    "TokenError",
    "camera",
    "camera_async",
    "list_cameras",
    "list_cameras_async",
    "load_credentials",
    "login",
]
