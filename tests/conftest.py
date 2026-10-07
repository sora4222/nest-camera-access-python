"""Shared test fixtures."""

import pytest


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
