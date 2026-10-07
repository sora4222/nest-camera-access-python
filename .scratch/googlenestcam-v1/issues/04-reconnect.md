# 04: Reconnect after a drop

**What to build:** When the connection drops (Wi-Fi blip, Google closes it, peer state goes to `failed`), the Stream starts a new session for the same Camera by itself and Frames keep coming in the same loop. `cam.stream(retries=N)` sets how many tries in a row; after the last one fails, a clear error is raised from `frames()`.

**Blocked by:** 02

**Status:** ready-for-human (PR open)

- [x] `retries` has a sensible default and can be set.
- [x] After a drop, Frames start again with no change to the developer's loop.
- [x] A good reconnect resets the try count.
- [x] After N failed tries, a clear error is raised from `frames()`.
- [x] The old session is stopped at Google when a new one starts.
- [x] Unit tests drop the fake peer and check both paths.
- [x] `make check` and `make test` pass.
