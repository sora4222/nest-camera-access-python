"""Tests for the pull request title check."""

import pytest

from scripts.check_pr_title import title_problem


@pytest.mark.parametrize(
    "title",
    [
        "feat: audio from streams",
        "fix(stream): reconnect after a drop",
        "refactor: use one deque buffer for latest and every-frame mode",
        "ci: check pull request titles",
        "feat!: rename list_cameras",
        "chore: bump numpy to 2.5",
    ],
)
def test_good_titles_pass(title: str) -> None:
    """Lowercase Conventional Commit titles have no problem."""
    assert title_problem(title) is None


@pytest.mark.parametrize(
    "title",
    [
        "Add audio",
        "Feat: audio from streams",
        "FEAT: audio from streams",
        "feat: Audio from streams",
        "feat:audio from streams",
        "feat: ",
        "feature: audio from streams",
        "feat: audio from streams.",
        "feat(Stream): reconnect",
        "feat: add the OpenCV notebook",
        "refactor: use one buffer for Latest mode",
    ],
)
def test_bad_titles_fail(title: str) -> None:
    """Titles that break the rules give a reason."""
    assert title_problem(title)


def test_main_exits_non_zero_on_a_bad_title(capsys: pytest.CaptureFixture[str]) -> None:
    """The command line prints the reason and fails."""
    from scripts.check_pr_title import main

    assert main(["Add audio"]) == 1
    assert "feat" in capsys.readouterr().err


def test_main_exits_zero_on_a_good_title() -> None:
    """The command line passes a good title."""
    from scripts.check_pr_title import main

    assert main(["feat: audio from streams"]) == 0
