"""Save and load the Token (the long-lived refresh token)."""

import json
import os
from pathlib import Path

from googlenestcam import settings
from googlenestcam.errors import TokenError


TOKEN_FILE_NAME = "token.json"
type TokenPath = str | os.PathLike[str]


def find_token_path(path: TokenPath | None = None) -> Path:
    """Return where the Token is kept, using the first of these that applies.

    1. ``path``, if given.
    2. ``GOOGLENESTCAM_TOKEN_PATH``, if set.
    3. ``./token.json``, if it exists in the current folder.
    4. ``$XDG_CONFIG_HOME/googlenestcam/token.json`` (``~/.config`` by default).
    """
    chosen = path or os.environ.get(settings.ENV_PREFIX + "TOKEN_PATH")
    if chosen:
        return Path(chosen).expanduser()
    local = Path.cwd() / TOKEN_FILE_NAME
    if local.exists():
        return local
    config_home = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(config_home) / "googlenestcam" / TOKEN_FILE_NAME


def load_refresh_token(path: TokenPath | None = None) -> str | None:
    """Return the Token, or ``None`` if there is none yet.

    ``GOOGLENESTCAM_REFRESH_TOKEN`` (which may be an ``op://`` reference) wins
    over the file, so a Token can be copied to a server without a file.

    Raises:
        TokenError: If the Token file cannot be read.
    """
    from_environment = settings.read_setting("REFRESH_TOKEN")
    if from_environment:
        return from_environment
    path = find_token_path(path)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())["refresh_token"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise TokenError(f"Cannot read the Token file {path}: {error}") from error


def save_refresh_token(refresh_token: str, path: TokenPath | None = None) -> Path:
    """Save the Token so only the current user can read it.

    Returns:
        The path the Token was saved to.
    """
    path = find_token_path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w") as file:
        json.dump({"refresh_token": refresh_token}, file)
    path.chmod(0o600)
    return path
