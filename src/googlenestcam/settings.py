"""Read googlenestcam settings from environment variables."""

import os
import warnings

from googlenestcam.errors import OnePasswordError
from googlenestcam.onepassword import resolve_reference

ENV_PREFIX = "GOOGLENESTCAM_"
ONE_PASSWORD_PREFIX = "op://"


def read_setting(name: str) -> str | None:
    """Return the ``GOOGLENESTCAM_<NAME>`` environment value, or ``None``.

    Values starting with ``op://`` are read from 1Password. If that fails, a
    warning is given and ``None`` is returned.
    """
    variable = ENV_PREFIX + name
    value = os.environ.get(variable)
    if not value or not value.startswith(ONE_PASSWORD_PREFIX):
        return value or None
    try:
        return resolve_reference(value)
    except OnePasswordError as error:
        warnings.warn(f"{variable}: {error}", UserWarning, stacklevel=2)
        return None
