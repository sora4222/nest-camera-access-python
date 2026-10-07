"""Tests for catching Google's redirect on this machine."""

import socket
import threading

import httpx
import pytest

from googlenestcam.errors import LoginError
from googlenestcam.redirect_receiver import RedirectReceiver


def test_receives_the_redirect_address() -> None:
    """The address Google redirects to is handed back."""
    with RedirectReceiver(port=0) as receiver:
        url = f"{receiver.redirect_uri}/?code=abc&state=s"
        thread = threading.Thread(target=httpx.get, args=(url,))
        thread.start()
        address = receiver.wait(timeout=5)
        thread.join()
    assert address.endswith("/?code=abc&state=s")
    assert receiver.redirect_uri.startswith("http://localhost:")


def test_ignores_requests_without_code_or_error() -> None:
    """Browser extras like /favicon.ico do not end the wait."""
    with RedirectReceiver(port=0) as receiver:

        def browse() -> None:
            httpx.get(f"{receiver.redirect_uri}/favicon.ico")
            httpx.get(f"{receiver.redirect_uri}/?error=access_denied")

        thread = threading.Thread(target=browse)
        thread.start()
        address = receiver.wait(timeout=5)
        thread.join()
    assert "error=access_denied" in address


def test_timeout_raises_login_error() -> None:
    """Waiting too long gives a clear error."""
    with RedirectReceiver(port=0) as receiver:
        with pytest.raises(LoginError, match="timed out"):
            receiver.wait(timeout=0.1)


def test_idle_browser_connection_does_not_block_the_redirect() -> None:
    """Browsers open spare connections early; the redirect still gets through."""
    with RedirectReceiver(port=0) as receiver:
        port = int(receiver.redirect_uri.rsplit(":", 1)[1])
        with socket.create_connection(("127.0.0.1", port)):
            url = f"{receiver.redirect_uri}/?code=abc&state=s"
            thread = threading.Thread(target=httpx.get, args=(url,), daemon=True)
            thread.start()
            address = receiver.wait(timeout=2)
    assert address.endswith("/?code=abc&state=s")
