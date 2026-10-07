"""Optional lookup of ``op://`` references through a 1Password service account.

Needs the ``googlenestcam[onepassword]`` extra. Every failure becomes a
``OnePasswordError`` so a 1Password problem never crashes the caller.
"""

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from googlenestcam.errors import OnePasswordError

SERVICE_ACCOUNT_ENV = "OP_SERVICE_ACCOUNT_TOKEN"


def resolve_reference(reference: str) -> str:
    """Return the secret an ``op://`` reference points to.

    Raises:
        OnePasswordError: If the extra, the service account token or the
            lookup fails.
    """
    service_account_token = os.environ.get(SERVICE_ACCOUNT_ENV)
    if not service_account_token:
        raise OnePasswordError(f"Set {SERVICE_ACCOUNT_ENV} to read {reference}")
    try:
        from onepassword.client import Client
    except ImportError as error:
        raise OnePasswordError(
            "Install googlenestcam[onepassword] to read op:// references"
        ) from error

    async def lookup() -> str:
        client = await Client.authenticate(
            auth=service_account_token,
            integration_name="googlenestcam",
            integration_version="0.1.0",
        )
        return await client.secrets.resolve(reference)

    try:
        # A separate thread keeps this working inside Jupyter's running loop.
        with ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(lambda: asyncio.run(lookup())).result()
    except Exception as error:
        raise OnePasswordError(f"Could not read {reference}: {error}") from error
