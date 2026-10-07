# 06: Frame helpers for Pillow and JPEG

**What to build:** A developer can call `frame.to_pil()` to get a Pillow RGB image and `frame.to_jpeg(quality=...)` to get JPEG bytes. Pillow comes from the new `[images]` extra and is only imported inside these helpers.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] `to_pil()` returns a Pillow RGB image the same size as `.image`.
- [ ] `to_jpeg(quality=...)` returns JPEG bytes.
- [ ] Without Pillow: clear error that says to install `googlenestcam[images]`. No error on import.
- [ ] `[images]` extra added; base install still has no Pillow.
- [ ] Unit tests.
- [ ] `make check` and `make test` pass.
