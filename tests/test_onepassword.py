"""Tests for the optional 1Password lookup."""

import sys

import pytest

from googlenestcam.errors import OnePasswordError
from googlenestcam.onepassword import resolve_reference


def test_missing_extra_raises_clear_error(monkeypatch) -> None:
    """Without the extra installed, the error says how to install it."""
    monkeypatch.setitem(sys.modules, "onepassword", None)
    monkeypatch.setitem(sys.modules, "onepassword.client", None)
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "token")
    with pytest.raises(OnePasswordError, match=r"googlenestcam\[onepassword\]"):
        resolve_reference("op://vault/item/field")


def test_missing_service_account_token_raises_clear_error() -> None:
    """Without a service account token, the error names the variable."""
    with pytest.raises(OnePasswordError, match="OP_SERVICE_ACCOUNT_TOKEN"):
        resolve_reference("op://vault/item/field")
