"""Tests for the Frame helpers that use Pillow."""

import io
import subprocess
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from googlenestcam import MissingExtraError
from googlenestcam.frame import Frame


def make_frame() -> Frame:
    """A 4 x 6 Frame with a red top-left pixel."""
    image = np.zeros((4, 6, 3), dtype=np.uint8)
    image[0, 0] = (255, 0, 0)
    return Frame(image, datetime.now(UTC))


def hide_pillow(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make ``import PIL`` fail as if Pillow were not installed."""
    for name in ("PIL", "PIL.Image"):
        monkeypatch.setitem(sys.modules, name, None)


def test_to_pil_gives_rgb_image_of_same_size() -> None:
    """``to_pil()`` returns a Pillow RGB image with the Frame's pixels."""
    picture = make_frame().to_pil()
    assert isinstance(picture, Image.Image)
    assert picture.mode == "RGB"
    assert picture.size == (6, 4)
    assert picture.getpixel((0, 0)) == (255, 0, 0)


def test_to_jpeg_gives_jpeg_bytes() -> None:
    """``to_jpeg()`` returns bytes Pillow reads back as a JPEG."""
    data = make_frame().to_jpeg()
    assert data.startswith(b"\xff\xd8")
    with Image.open(io.BytesIO(data)) as picture:
        assert picture.format == "JPEG"
        assert picture.size == (6, 4)


def test_to_jpeg_quality_changes_size() -> None:
    """A higher quality gives a bigger JPEG."""
    rng = np.random.default_rng(0)
    image = rng.integers(0, 256, (64, 64, 3), dtype=np.uint8)
    frame = Frame(image, datetime.now(UTC))
    assert len(frame.to_jpeg(quality=95)) > len(frame.to_jpeg(quality=10))


@pytest.mark.parametrize("helper", ["to_pil", "to_jpeg"])
def test_helpers_without_pillow_say_what_to_install(
    monkeypatch: pytest.MonkeyPatch, helper: str
) -> None:
    """Without Pillow the helpers name the extra to install."""
    hide_pillow(monkeypatch)
    with pytest.raises(MissingExtraError, match=r"googlenestcam\[images\]"):
        getattr(make_frame(), helper)()


def test_missing_extra_error_is_an_import_error() -> None:
    """Code that catches ImportError also catches a missing extra."""
    assert issubclass(MissingExtraError, ImportError)


def test_importing_package_does_not_import_pillow() -> None:
    """``import googlenestcam`` leaves Pillow unloaded."""
    code = "import sys, googlenestcam; print('PIL' in sys.modules)"
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "False"


def test_base_install_has_no_pillow() -> None:
    """Pillow is only in the ``images`` extra."""
    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    project = tomllib.loads(pyproject.read_text())["project"]
    assert not any(d.lower().startswith("pillow") for d in project["dependencies"])
    images = project["optional-dependencies"]["images"]
    assert any(d.lower().startswith("pillow") for d in images)
