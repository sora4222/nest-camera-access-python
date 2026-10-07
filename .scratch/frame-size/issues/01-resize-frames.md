# 01: Resize Frames with `size=(width, height)`

**What to build:** `stream()`, `stream_async()`, `snapshot()` and `snapshot_async()` take `size=(width, height)`. Each Frame is resized to that size before the developer gets it. See [spec.md](../spec.md).

**Blocked by:** none

**Status:** ready-for-human

- [x] Stream Frames have the asked size; reconnects keep it.
- [x] Snapshot Frames have the asked size.
- [x] No `size` keeps the Camera's size.
- [x] Bad sizes raise `ValueError`.
- [x] Docs: design.md and GLOSSARY.md.
- [x] Unit tests.
- [x] `make check` and `make test` pass.
