# 05: Snapshot

**What to build:** `cam.snapshot()` and `await cam.snapshot_async()` give one Frame. They open a Stream with Audio off, wait for the first Frame, and close it. The docstring and design doc say it is slow and to use a Stream for many Frames.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] Returns one Frame.
- [ ] The Stream is always stopped at Google, even on error or timeout.
- [ ] Clear timeout error if no Frame arrives; timeout can be set.
- [ ] Docstring and design doc say it is slow.
- [ ] Unit tests with the fake-Google kit; one `real_camera` test.
- [ ] `make check` and `make test` pass.
