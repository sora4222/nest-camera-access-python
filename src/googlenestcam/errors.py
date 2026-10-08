"""Errors raised by googlenestcam."""


class GoogleNestCamError(Exception):
    """Base class for every googlenestcam error."""


class CredentialsError(GoogleNestCamError):
    """Credentials are missing or could not be read."""


class OnePasswordError(GoogleNestCamError):
    """A value could not be read from 1Password."""


class LoginError(GoogleNestCamError):
    """The Login did not finish."""


class TokenError(GoogleNestCamError):
    """The Token is broken, revoked or could not be used."""


class MissingTokenError(TokenError):
    """No Token exists yet; run ``googlenestcam.login()``."""


class GoogleApiError(GoogleNestCamError):
    """Google's Smart Device Management API refused a request."""


class CameraNotFoundError(GoogleNestCamError):
    """No single Camera matches the given name or ID."""


class StreamError(GoogleNestCamError):
    """A Stream could not start or stopped working."""


class CameraOffError(StreamError):
    """The Camera is turned off or offline, so Google will not stream it.

    Google's API cannot tell if a Camera is on, or turn it on. Turn it on in
    the Google Home app.
    """


class SnapshotTimeoutError(StreamError, TimeoutError):
    """No Frame arrived in time for a Snapshot."""


class MissingExtraError(GoogleNestCamError, ImportError):
    """An optional extra, such as ``googlenestcam[images]``, is not installed."""
