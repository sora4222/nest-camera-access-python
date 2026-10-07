.PHONY: test test_real_cameras check build

# Unit tests with fake Google replies. Runs anywhere.
test:
	uv run pytest -m "not real_camera"

# Tests against real Cameras. Needs a Token and Credentials; never run in CI.
# Exit code 5 (no tests collected) is not a failure.
test_real_cameras:
	uv run pytest -m real_camera || [ $$? -eq 5 ]

# Formatting, linting and type checking.
check:
	uv run ruff format --check .
	uv run ruff check .
	uv run --extra onepassword ty check

# Build the wheel and source package into dist/ for other projects to install.
build:
	rm -rf dist
	uv build
