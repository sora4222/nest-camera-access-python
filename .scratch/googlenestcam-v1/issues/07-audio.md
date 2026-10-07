# 07: Audio

**What to build:** Audio is on by default. `s.audio()` gives Audio chunks with `.samples` (NumPy, 48 kHz) and `.time` on the same clock as Frame time. `cam.stream(audio=False)` turns it off and saves CPU. `frames()` and `audio()` can be read at the same time from two threads. Unread Audio is kept only for the last few seconds, so leaving it on never fills memory. Fix the design doc sketch to show the two-thread way.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] `cam.stream()` has Audio on; `audio=False` turns it off and Audio is not decoded.
- [ ] Chunks have `.samples` at 48 kHz and `.time` on the same clock as `Frame.time`.
- [ ] `frames()` and `audio()` work together from two threads.
- [ ] Unread Audio is bounded; oldest chunks are dropped.
- [ ] `stream_async()` has the same Audio.
- [ ] Design doc shows reading Frames and Audio in two threads.
- [ ] Unit tests with the fake-Google kit sending made-up sound; one `real_camera` test.
- [ ] `make check` and `make test` pass.
