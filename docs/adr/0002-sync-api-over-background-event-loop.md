# Normal (sync) API runs async code on a hidden background event loop

WebRTC (`aiortc`) and Google's API calls are async, but most PyTorch, TensorFlow and OpenCV code is not. The public API is therefore sync first (`cam.snapshot()`, `with cam.stream() as s`), backed by one background thread running an event loop that the package owns. Async versions (`snapshot_async`, `stream_async`) are also public for async callers. A background loop also means the sync API works inside Jupyter, which already runs its own event loop, where `asyncio.run` would fail.

## Consequences

- Streams keep running between calls, so Frames and Audio chunks are buffered in the background, not pulled on demand.
- Closing a Stream (leaving the `with` block) must reach the background loop so Google's media session is stopped.
