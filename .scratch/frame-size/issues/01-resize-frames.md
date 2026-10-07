# 01: Resize Frames with `size=(width, height)`

**What to build:** `stream()`, `stream_async()`, `snapshot()` and `snapshot_async()` take `size=(width, height)`. Each Frame is resized to that size before the developer gets it. See [spec.md](../spec.md).

**Blocked by:** none

**Status:** ready-for-agent

- [ ] Stream Frames have the asked size; reconnects keep it.
- [ ] Snapshot Frames have the asked size.
- [ ] No `size` keeps the Camera's size.
- [ ] Bad sizes raise `ValueError`.
- [ ] Docs: design.md and GLOSSARY.md.
- [ ] Unit tests.
- [ ] `make check` and `make test` pass.
