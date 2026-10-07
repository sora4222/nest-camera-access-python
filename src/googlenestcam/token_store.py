"""Save and load the Token (the long-lived refresh token)."""

import json
import os
from pathlib import Path

from googlenestcam import settings
from googlenestcam.errors import TokenError


def default_token_path() -> Path:
    """Return where the Token is kept.

    ``GOOGLENESTCAM_TOKEN_PATH`` if set, otherwise
    ``$XDG_CONFIG_HOME/googlenestcam/token.json`` (``~/.config`` by default).
    """
    override = os.environ.get(settings.ENV_PREFIX + "TOKEN_PATH")
    if override:
        return Path(override).expanduser()
    config_home = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(config_home) / "googlenestcam" / "token.json"


def load_refresh_token(path: Path | None = None) -> str | None:
    """Return the Token, or ``None`` if there is none yet.

    ``GOOGLENESTCAM_REFRESH_TOKEN`` (which may be an ``op://`` reference) wins
    over the file, so a Token can be copied to a server without a file.

    Raises:
        TokenError: If the Token file cannot be read.
    """
    from_environment = settings.read_setting("REFRESH_TOKEN")
    if from_environment:
        return from_environment
    path = path or default_token_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())["refresh_token"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise TokenError(f"Cannot read the Token file {path}: {error}") from error


def save_refresh_token(refresh_token: str, path: Path | None = None) -> Path:
    """Save the Token so only the current user can read it.

    Returns:
        The path the Token was saved to.
    """
    path = path or default_token_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w") as file:
        json.dump({"refresh_token": refresh_token}, file)
    path.chmod(0o600)
    return path
