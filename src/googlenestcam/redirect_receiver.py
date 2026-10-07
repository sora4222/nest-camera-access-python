"""Catch Google's Login redirect on a local web server."""

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import TracebackType
from typing import Self

from googlenestcam.errors import LoginError

DONE_PAGE = b"<html><body><p>Login finished. You can close this tab.</p></body></html>"


class RedirectReceiver:
    """A one-shot web server on ``localhost`` that waits for Google's redirect."""

    def __init__(self, port: int = 8080) -> None:
        """Prepare a receiver on ``port`` (0 picks a free port)."""
        self._port = port
        self._address: str | None = None
        self._received = threading.Event()
        self._server: ThreadingHTTPServer | None = None

    @property
    def redirect_uri(self) -> str:
        """The address to give Google as the redirect URI."""
        if self._server is None:
            raise RuntimeError("RedirectReceiver is not started")
        return f"http://localhost:{self._server.server_port}"

    def __enter__(self) -> Self:
        """Start listening on 127.0.0.1 only.

        One thread per connection, so a spare connection a browser opens early
        cannot block the redirect.
        """
        receiver = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if "code=" not in self.path and "error=" not in self.path:
                    self.send_error(404)
                    return
                receiver._address = receiver.redirect_uri + self.path
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(DONE_PAGE)
                receiver._received.set()

            def log_message(self, format: str, *args: object) -> None:
                pass

        try:
            self._server = ThreadingHTTPServer(("127.0.0.1", self._port), Handler)
        except OSError as error:
            raise LoginError(f"Cannot listen on port {self._port}: {error}") from error
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Stop the server."""
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()

    def wait(self, timeout: float) -> str:
        """Return the full redirect address once Google sends the browser back.

        Raises:
            LoginError: If nothing arrives within ``timeout`` seconds.
        """
        if not self._received.wait(timeout) or self._address is None:
            raise LoginError(f"Login timed out after {timeout:g} seconds")
        return self._address
