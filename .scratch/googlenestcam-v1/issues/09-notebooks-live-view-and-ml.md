# 09: Notebooks: Live view and PyTorch, TensorFlow, OpenCV

**What to build:** Notebook 2 shows a live view inside Jupyter. Notebook 3 feeds Frames to PyTorch, TensorFlow and OpenCV. Both very short. Notebook 3 says how to install PyTorch or TensorFlow yourself; they are in no extra.

**Blocked by:** 06, 08

**Status:** ready-for-human

- [x] Saved with no outputs, Tokens or Camera IDs.
- [ ] Each runs top to bottom with a real Camera.
- [x] Notebook 3 skips a section cleanly if PyTorch or TensorFlow is not installed.

**Notes:** Notebooks are `notebooks/02-live-view.ipynb` and `notebooks/03-machine-learning.ipynb`. There was no real Camera when this was built, so they were not run; a human must run both top to bottom (`uv run --extra notebooks jupyter lab`) and save them again with no outputs. `ty` now checks the notebooks with the `[notebooks]` extra, and treats `torch` and `tensorflow` as allowed missing imports.
