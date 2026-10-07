# 01: Camera list

**What to build:** A developer who has done Login can call `gnc.list_cameras()` and see every Camera on their account with its Google Home name and Google ID. `gnc.camera("Front door")` or `gnc.camera("<id>")` gives back that Camera. This works as a normal sync call, in a script and inside Jupyter, because it runs on the package's hidden background event loop (ADR 0002), which this ticket builds. Includes the small SDM client (list devices, run a device command) using the existing `GoogleAuth`, and the advanced `transport=` keyword so tests can use a fake Google.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `list_cameras()` returns every Camera that supports WebRTC, each with `.name` and `.id`.
- [ ] RTSP-only Cameras and non-camera devices are left out.
- [ ] Name falls back to the room name when the custom name is empty.
- [ ] `camera()` finds a Camera by short ID, full `enterprises/.../devices/...` ID, or name.
- [ ] Unknown name: clear error that lists the names that exist.
- [ ] Two Cameras with the same name: clear error that lists their IDs.
- [ ] No Token: the existing `on_missing_token` behaviour applies (Login or `MissingTokenError`).
- [ ] Google errors become a package error with Google's message.
- [ ] Sync call works inside a running event loop (as in Jupyter).
- [ ] Unit tests through the public API with a fake httpx transport; one `real_camera` test.
- [ ] `make check` and `make test` pass.
