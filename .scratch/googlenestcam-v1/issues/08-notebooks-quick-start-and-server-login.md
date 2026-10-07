# 08: Notebooks: Quick start and Server login

**What to build:** Add the `[notebooks]` extra (Jupyter, OpenCV, Matplotlib, Pillow), only installed when asked for. Write notebook 1, Quick start (Login, list Cameras, take a Snapshot; very short), and notebook 4, Server login (Login with no browser, plus the SSH tunnel and copy-the-Token options). README links the notebooks.

**Blocked by:** 05

**Status:** resolved (needs a human check with a real Camera)

- [x] `pip install googlenestcam` does not install notebook tools.
- [x] `pip install googlenestcam[notebooks]` is enough to run both notebooks.
- [x] Notebooks are saved with no outputs, Tokens or Camera IDs.
- [ ] Each runs top to bottom with a real Camera.
- [x] README links the notebooks.

**Notes:** Notebooks are `notebooks/01-quick-start.ipynb` and `notebooks/04-server-login.ipynb`, numbered so all seven sort in order. There was no real Camera when this was built, so the notebooks were not run; a human must run both top to bottom (`uv run --extra notebooks jupyter lab`) and save them again with no outputs. Ruff formats and lints the notebooks with no exclusion.
