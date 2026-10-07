"""Shared test fixtures."""

from collections.abc import Iterator

import pytest

from googlenestcam import background_loop
from googlenestcam.camera import Camera
from googlenestcam.credentials import Credentials
from googlenestcam.nest import Nest
from googlenestcam.token_store import save_refresh_token
from tests.fake_google import FakeGoogle


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch, tmp_path, request):
    """Keep unit tests away from real settings, Tokens and 1Password.

    Tests marked ``real_camera`` keep the real environment.
    """
    if request.node.get_closest_marker("real_camera"):
        return
    import os

    for name in list(os.environ):
        if name.startswith("GOOGLENESTCAM_") or name == "OP_SERVICE_ACCOUNT_TOKEN":
            monkeypatch.delenv(name)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)


@pytest.fixture
def google() -> Iterator[FakeGoogle]:
    """A fake Google; its peers are closed after the test."""
    fake = FakeGoogle()
    yield fake
    background_loop.run(fake.close())


@pytest.fixture
def camera(google, tmp_path) -> Camera:
    """The fake Google's "Front door" Camera."""
    path = tmp_path / "token.json"
    save_refresh_token("r", path)
    nest = Nest(
        credentials=Credentials("id", "secret", "project"),
        token_path=path,
        transport=google.transport,
    )
    return nest.camera("Front door")
