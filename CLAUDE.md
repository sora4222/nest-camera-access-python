# Nest Camera Python

This is a Python module intended to allow the Python developer to quickly access their Google Nest Cameras.
A Jupyter notebook should be written to show to developers how they can use the module to get a stream, a photo or any of the other Google Nest basic functionality
This module should be handling the authentication, the Google Nest WebRTC, and any of the other functionality through easy to use coding structure, allowing more complex parameters only if the developer wants to access them.

## Development rules

Keep things simple, the user should be able to access images, the WebRTC and the cameras other abilities in as few lines as possible.

1. Python files, functions and classes must always be kept single responsibility.
2. Write docstring for files and public functions. Documentation must be kept concise.
3. The README.md should link to other files and only address what the module does, and the basics of how it does it. More complex instructions should be in docstrings or the `docs/`.
4. Keep typing clean and target Python 3.12+
5. May install other dependencies, but keep this short and the code secure
6. Take a Test Driven Development approach


## Python tooling

Use uv for every Python command in this project.

- Run scripts and tools with `uv run`, never bare `python` or `python3`.
- Add and remove dependencies with `uv add` and `uv remove`, never `pip install`.
- Sync and lock the environment with `uv sync` and `uv lock`.
- Run a one-off tool without adding it to the project: `uvx ruff check`.
- For a standalone script, use `uv run script.py` and add its dependencies with
  `uv add --script script.py <package>`.

Use `ruff` for formatting and linting Python files, and `ty` for static type checking
Pytest should be used for testing
