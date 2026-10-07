# 03: Every-frame mode

**What to build:** A developer who must not miss a Frame calls `cam.stream(frames="all")` and gets every Frame in order. They can set `queue_size`. When the queue is full, the next read raises a clear error by default, or with `on_full="drop_oldest"` the oldest Frame is dropped, a warning is given once, and `s.dropped` counts the drops.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] `frames="latest"` stays the default; `frames="all"` gives every Frame in order.
- [ ] `queue_size` can be set.
- [ ] Full queue raises a clear error from `frames()` by default.
- [ ] `on_full="drop_oldest"` drops the oldest, warns once, and `s.dropped` gives the count.
- [ ] Unit tests use the fake-Google kit sending fast and a slow reader.
- [ ] `make check` and `make test` pass.
