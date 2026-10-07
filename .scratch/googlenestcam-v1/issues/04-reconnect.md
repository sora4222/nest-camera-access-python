# 04: Reconnect after a drop

**What to build:** When the connection drops (Wi-Fi blip, Google closes it, peer state goes to `failed`), the Stream starts a new session for the same Camera by itself and Frames keep coming in the same loop. `cam.stream(retries=N)` sets how many tries in a row; after the last one fails, a clear error is raised from `frames()`.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] `retries` has a sensible default and can be set.
- [ ] After a drop, Frames start again with no change to the developer's loop.
- [ ] A good reconnect resets the try count.
- [ ] After N failed tries, a clear error is raised from `frames()`.
- [ ] The old session is stopped at Google when a new one starts.
- [ ] Unit tests drop the fake peer and check both paths.
- [ ] `make check` and `make test` pass.
