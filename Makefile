.PHONY: test test_real_cameras coverage login check build

# Load a local .env (never committed) for commands that talk to Google.
ENV_FILE := $(if $(wildcard .env),--env-file .env,)

# Unit tests with fake Google replies. Runs anywhere.
test:
	uv run --extra images pytest -m "not real_camera"

# Unit tests, then fail if under 80% of the lines this branch changed are tested.
# Compares with COMPARE_BRANCH (default origin/main).
COMPARE_BRANCH ?= origin/main
coverage:
	uv run --extra images pytest -m "not real_camera" --cov --cov-report=xml
	uv run diff-cover coverage.xml --compare-branch=$(COMPARE_BRANCH) --fail-under=80

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
	uv run --extra onepassword --extra notebooks ty check

# Build the wheel and source package into dist/ for other projects to install.
build:
	rm -rf dist
	uv build
