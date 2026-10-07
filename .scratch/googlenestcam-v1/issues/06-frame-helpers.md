# 06: Frame helpers for Pillow and JPEG

**What to build:** A developer can call `frame.to_pil()` to get a Pillow RGB image and `frame.to_jpeg(quality=...)` to get JPEG bytes. Pillow comes from the new `[images]` extra and is only imported inside these helpers.

**Blocked by:** 02

**Status:** resolved

- [x] `to_pil()` returns a Pillow RGB image the same size as `.image`.
- [x] `to_jpeg(quality=...)` returns JPEG bytes.
- [x] Without Pillow: clear error that says to install `googlenestcam[images]`. No error on import.
- [x] `[images]` extra added; base install still has no Pillow.
- [x] Unit tests.
- [x] `make check` and `make test` pass.

Notes: Pillow is imported only in `src/googlenestcam/pillow_image.py`; without it the helpers raise `MissingExtraError` (an `ImportError`). A human can check `cam.snapshot().to_jpeg()` on a real Camera.
