# Pull request checks

GitHub Actions runs these on every pull request:

- **ruff-fix** ([ci.yml](../.github/workflows/ci.yml)): runs `ruff format` and `ruff check --fix`, and pushes any fixes to the pull request as a `style:` commit. It then starts the checks again for that commit. Pull requests from forks are not fixed.
- **check-and-test** ([ci.yml](../.github/workflows/ci.yml)): `make check`, `make test` (every test that runs without a real Camera) and `make build`.
- **pr-title** ([pr-title.yml](../.github/workflows/pr-title.yml)): the title must be a Conventional Commit with no capital letters, for example `feat: audio from streams` or `fix(stream): reconnect after a drop`. Allowed types are in [scripts/check_pr_title.py](../scripts/check_pr_title.py).

Real Camera tests (`make test_real_cameras`) never run in GitHub.

## Merge commit text

Pull requests are squash merged and the commit text is the pull request title. This is a repo setting: **Settings → General → Pull Requests**:

1. Tick **Allow squash merging** and set its default message to **Pull request title**.
2. Untick **Allow merge commits** and **Allow rebase merging**.
