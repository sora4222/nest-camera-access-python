"""The one-time Login that saves the Token."""

import secrets
import webbrowser
from collections.abc import Callable
from pathlib import Path
from typing import Literal

import httpx

from googlenestcam.credentials import Credentials, load_credentials
from googlenestcam.oauth import authorization_url, code_from_address, exchange_code
from googlenestcam.redirect_receiver import RedirectReceiver
from googlenestcam.token_store import TokenPath, save_refresh_token

LoginMode = Literal["browser", "server"]
SERVER_REDIRECT_URI = "https://www.google.com"


def login(
    mode: LoginMode = "browser",
    *,
    client_id: str | None = None,
    client_secret: str | None = None,
    project_id: str | None = None,
    credentials: Credentials | None = None,
    token_path: TokenPath | None = None,
    port: int = 8080,
    redirect_uri: str | None = None,
    timeout: float = 300,
    open_url: Callable[[str], bool] = webbrowser.open,
    show: Callable[[str], object] = print,
    ask: Callable[[str], str] = input,
) -> Path:
    """Log in to Google once and save the Token.

    Args:
        mode: ``"browser"`` catches Google's redirect on ``http://localhost:<port>``
            (also works over an SSH tunnel). ``"server"`` is for machines with
            no browser: approve on another device, then paste the address.
        client_id: OAuth client ID; see ``load_credentials`` for defaults.
        client_secret: OAuth client secret.
        project_id: Device Access project ID.
        credentials: Ready-made Credentials, instead of the three values.
        token_path: Where to save the Token; see ``find_token_path``.
        port: Local port the ``"browser"`` mode server listens on.
        redirect_uri: Where Google sends the browser after you approve. It
            must be on your OAuth client. ``None`` uses
            ``http://localhost:<port>`` in ``"browser"`` mode and
            ``https://www.google.com`` in ``"server"`` mode. In
            ``"browser"`` mode it must reach the server on ``port``, for
            example through a tunnel; to use another web application, use
            ``"server"`` mode and paste the address it lands on.
        timeout: Seconds to wait for the browser in ``"browser"`` mode.
        open_url: Opens a URL in a browser.
        show: Shows a line to the developer.
        ask: Asks the developer for a line of text.

    Returns:
        The path the Token was saved to.

    Raises:
        LoginError: If the Login does not finish.
        CredentialsError: If Credentials are missing.
        ValueError: If ``mode`` or ``redirect_uri`` is not allowed.
    """
    if mode not in ("browser", "server"):
        raise ValueError('mode must be "browser" or "server"')
    if redirect_uri is not None and not redirect_uri.startswith(
        ("http://", "https://")
    ):
        raise ValueError("redirect_uri must start with http:// or https://")
    credentials = credentials or load_credentials(client_id, client_secret, project_id)
    state = secrets.token_urlsafe(16)

    if mode == "server":
        redirect_uri = redirect_uri or SERVER_REDIRECT_URI
        show("Open this link on any device and approve access:")
        show(authorization_url(credentials, redirect_uri, state))
        address = ask("Then paste the address of the page you land on here: ")
    else:
        with RedirectReceiver(port) as receiver:
            redirect_uri = redirect_uri or receiver.redirect_uri
            url = authorization_url(credentials, redirect_uri, state)
            show(f"Opening Google login. If no browser opens, visit:\n{url}")
            open_url(url)
            address = receiver.wait(timeout)

    code = code_from_address(address, state)
    with httpx.Client(timeout=20) as client:
        refresh_token = exchange_code(credentials, code, redirect_uri, client)
    path = save_refresh_token(refresh_token, token_path)
    show(f"Logged in. Token saved to {path}")
    return path
