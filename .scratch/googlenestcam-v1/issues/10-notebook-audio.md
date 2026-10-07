# 10: Notebook: Audio

**What to build:** Notebook 5 reads Audio chunks and Frames in two threads, matches them by time, and shows passing samples to a tool like Whisper.

**Blocked by:** 07, 08

**Status:** ready-for-human

- [x] Saved with no outputs, Tokens or Camera IDs.
- [ ] Runs top to bottom with a real Camera.

**Notes:** Notebook is `notebooks/05-audio.ipynb`. It runs Whisper only if you install it yourself (`pip install openai-whisper`); `ty` allows `whisper` to be missing. There was no real Camera when this was built, so it was not run; a human must run it top to bottom and save it again with no outputs.
