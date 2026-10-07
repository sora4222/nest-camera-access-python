# 12: Frame queue on deque

**What to build:** Replace the two hand-written Frame holders (`LatestFrame` and `FrameQueue`) with one `FrameBuffer` built on `collections.deque(maxlen=...)`, so there is less custom code to maintain. Public behaviour does not change, except that drops are now logged instead of raised as a Python warning (asked in review).

**Blocked by:** 03

**Status:** ready-for-human (PR open)

- [x] Latest mode is a deque with `maxlen=1`; a new Frame quietly replaces an unread one.
- [x] Every-frame mode is a deque with `maxlen=queue_size`.
- [x] `on_full="raise"` (default) still makes the next read raise a clear error.
- [x] `on_full="drop_oldest"` lets the deque drop the oldest and counts in `s.dropped`.
- [x] Drops are logged, not warned: the first at warning level, later ones at debug, on the `googlenestcam` logger.
- [x] The package logger has only a `NullHandler`, so the developer's logging setup decides what is shown.
- [x] Snapshot uses the same buffer.
- [x] `make check` and `make test` pass.

## Comments

`queue.Queue` was not used: it cannot drop the oldest item, and it has no way to wake a waiting reader on close before Python 3.13 (`Queue.shutdown`). A deque plus one `threading.Condition` keeps both modes.
