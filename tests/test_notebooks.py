"""Checks the notebooks are clean and the notebook tools stay optional."""

import importlib
import json
import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = sorted((ROOT / "notebooks").glob("*.ipynb"))
EXPECTED = ["01-quick-start.ipynb", "04-server-login.ipynb"]
NOTEBOOK_TOOLS = ("jupyter", "opencv", "matplotlib", "pillow")
CAMERA_ID = re.compile(r"enterprises/[^/\s\"']+/devices/[^/\s\"']+")
TOKEN = re.compile(r"\bya29\.|\b1//0[\w-]{10,}")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _code(notebook: dict) -> list[str]:
    return [
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    ]


def test_planned_notebooks_exist() -> None:
    """Notebooks 1 and 4 are in `notebooks/`, named to sort in order."""
    names = [path.name for path in NOTEBOOKS]
    assert all(name in names for name in EXPECTED)


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda path: path.name)
def test_notebook_is_valid(path: Path) -> None:
    """Each notebook is nbformat 4 JSON, checked by nbformat when installed."""
    notebook = _load(path)
    try:
        nbformat = importlib.import_module("nbformat")
    except ImportError:  # The [notebooks] extra is not installed.
        pass
    else:
        nbformat.validate(nbformat.from_dict(notebook))
    assert notebook["nbformat"] == 4
    assert notebook["cells"]


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda path: path.name)
def test_notebook_has_no_outputs(path: Path) -> None:
    """Notebooks are saved with no outputs or run counts."""
    for cell in _load(path)["cells"]:
        if cell["cell_type"] == "code":
            assert cell["outputs"] == []
            assert cell["execution_count"] is None


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda path: path.name)
def test_notebook_code_compiles(path: Path) -> None:
    """Every code cell is valid Python."""
    for index, source in enumerate(_code(_load(path))):
        compile(source, f"{path.name}[{index}]", "exec")


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda path: path.name)
def test_notebook_has_no_secrets(path: Path) -> None:
    """No Camera IDs or Google Tokens are saved in a notebook."""
    text = path.read_text(encoding="utf-8")
    assert not CAMERA_ID.search(text)
    assert not TOKEN.search(text)


def test_notebook_tools_are_only_in_the_extra() -> None:
    """Jupyter, OpenCV, Matplotlib and Pillow come only with `[notebooks]`."""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    base = " ".join(project["dependencies"]).lower()
    extra = " ".join(project["optional-dependencies"]["notebooks"]).lower()
    for tool in NOTEBOOK_TOOLS:
        assert tool not in base
        assert tool in extra
