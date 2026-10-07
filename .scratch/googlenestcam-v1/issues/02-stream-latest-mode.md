# 02: Stream in Latest mode

**What to build:** The first full path to live pictures. `with cam.stream() as s: for frame in s.frames(): ...` gives live Frames in Latest mode, and `async with cam.stream_async()` does the same for async code. Each Frame has `.image` (NumPy, H × W × 3, RGB, uint8) and `.time`. The Stream keeps going past 5 minutes and is stopped at Google when the `with` block ends. Adds `aiortc` and `numpy` to the base install.

Copy from `video-stream`'s streaming code: the Nest offer builder and its checks, the blank ICE candidate fix for Google's answer, the extend loop (60 s before `expiresAt`), and the close order. The audio track is in the offer (Google needs it) but its packets are thrown away for now; ticket 07 adds Audio.

Also builds the **fake-Google test kit** later tickets reuse: a fake httpx transport that answers `GenerateWebRtcStream` with a small local aiortc peer sending made-up video over localhost.

**Blocked by:** 01

**Status:** ready-for-human (PR open; real Camera test not yet run)

- [x] `Frame` has `.image` and `.time`; `np.asarray(frame)` works.
- [x] Latest mode always gives the newest Frame; old ones are skipped.
- [x] Extend is called before expiry (fake Google gives a short `expiresAt`).
- [x] Leaving the `with` block calls `StopWebRtcStream` and closes the peer, also after an error inside the block.
- [x] Google refusing the stream gives a clear package error.
- [x] Works in a plain script and inside a running event loop (Jupyter).
- [x] `stream_async()` gives the same Frames.
- [x] Unit tests run with no internet, using the fake-Google kit; the fake answer has a blank candidate foundation.
- [ ] `real_camera` test reads a few Frames from a real Camera.
- [x] `make check` and `make test` pass.

## Comments

- Built in branch `claude/implement-spec-qbf2f2` on top of the Camera list PR. The `real_camera` test is written but needs Jesse to run `make test_real_cameras`.
