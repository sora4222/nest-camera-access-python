"""Check that a pull request title is an all-lowercase Conventional Commit.

The title becomes the squash merge commit, so it must read like one:
``type(optional-scope)!: subject``, with no capital letters anywhere.

Usage: ``uv run scripts/check_pr_title.py "feat: audio from streams"``.
"""

import re
import sys

TYPES = (
    "feat",
    "fix",
    "chore",
    "ci",
    "test",
    "refactor",
    "docs",
    "style",
    "perf",
    "build",
    "revert",
)

_PATTERN = re.compile(
    r"^(?P<type>[a-z]+)(\((?P<scope>[a-z0-9_./-]+)\))?!?: (?P<subject>\S.*)$"
)


def title_problem(title: str) -> str | None:
    """Return why ``title`` is not allowed, or ``None`` if it is fine."""
    match = _PATTERN.match(title)
    if match is None:
        return "Title must look like `feat: subject` or `fix(scope): subject`."
    if match["type"] not in TYPES:
        return f"Type `{match['type']}` is not one of: {', '.join(TYPES)}."
    if title != title.lower():
        return "Title must have no capital letters."
    subject = match["subject"]
    if subject.endswith("."):
        return "Subject must not end with a full stop."
    return None


def main(argv: list[str]) -> int:
    """Check the title given as the first argument; return the exit code."""
    title = argv[0] if argv else ""
    problem = title_problem(title)
    if problem is None:
        print(f"OK: {title}")
        return 0
    print(
        f"Bad pull request title: {title!r}\n{problem}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
