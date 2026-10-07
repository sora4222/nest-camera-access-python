.PHONY: test test_real_cameras login check build

# Load a local .env (never committed) for commands that talk to Google.
ENV_FILE := $(if $(wildcard .env),--env-file .env,)

# Unit tests with fake Google replies. Runs anywhere.
test:
	uv run pytest -m "not real_camera"

# Tests against real Cameras. Needs a Token and Credentials; never run in CI.
# -rs prints why a test was skipped. Exit code 5 (no tests collected) is not a failure.
test_real_cameras:
	uv run $(ENV_FILE) pytest -m real_camera -rs || [ $$? -eq 5 ]

# One-time Login that saves the Token, using Credentials from .env.
login:
	uv run $(ENV_FILE) python -c "import googlenestcam; googlenestcam.login()"

# Formatting, linting and type checking.
check:
	uv run ruff format --check .
	uv run ruff check .
	uv run --extra onepassword ty check

# Build the wheel and source package into dist/ for other projects to install.
build:
	rm -rf dist
	uv build
