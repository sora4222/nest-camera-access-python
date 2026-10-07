"""Load the OAuth Credentials needed to talk to Google."""

from dataclasses import dataclass, field

from googlenestcam import settings
from googlenestcam.errors import CredentialsError


@dataclass(frozen=True)
class Credentials:
    """OAuth client ID, client secret and Device Access project ID."""

    client_id: str
    client_secret: str = field(repr=False)
    project_id: str


def load_credentials(
    client_id: str | None = None,
    client_secret: str | None = None,
    project_id: str | None = None,
) -> Credentials:
    """Build Credentials from arguments, then environment variables.

    Each missing argument is read from ``GOOGLENESTCAM_CLIENT_ID``,
    ``GOOGLENESTCAM_CLIENT_SECRET`` or ``GOOGLENESTCAM_PROJECT_ID``. Environment
    values may be ``op://`` 1Password references.

    Raises:
        CredentialsError: If any value is still missing.
    """
    values = {
        "client_id": client_id,
        "client_secret": client_secret,
        "project_id": project_id,
    }
    for name, value in values.items():
        if not value:
            values[name] = settings.read_setting(name.upper())
    missing = [name for name, value in values.items() if not value]
    if missing:
        hints = ", ".join(
            f"{name} (or {settings.ENV_PREFIX}{name.upper()})" for name in missing
        )
        raise CredentialsError(f"Missing Credentials: {hints}")
    return Credentials(
        client_id=str(values["client_id"]),
        client_secret=str(values["client_secret"]),
        project_id=str(values["project_id"]),
    )
