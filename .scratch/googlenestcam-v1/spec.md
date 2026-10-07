# Spec: googlenestcam version 1 (Cameras, Streams, Snapshots, Audio, notebooks)

Status: ready-for-agent

Words in **bold** are from `GLOSSARY.md`. Decisions are also in `docs/design.md` and `docs/adr/` (ADR 0001 Server login, ADR 0002 sync API over a background event loop).

## Problem Statement

A Python developer wants pictures and sound from their Google Nest **Cameras** to feed into PyTorch, TensorFlow, OpenCV or similar tools. Today the only working code is the `video-stream` app. It is an app, not a package. It needs 1Password, it is all async, it only gives JPEG bytes to a web page, and the cameras must be typed into an environment variable by their long Google ID. A developer cannot `pip install` it and get a NumPy array in a few lines.

**Login**, **Server login**, the **Token** and **Credentials** are already done in this package (PR #2). What is missing is everything after Login: finding Cameras, getting **Frames** and **Audio**, and showing developers how to use them.

## Solution

The `googlenestcam` package gets a small sync API, with matching async calls, and seven short Jupyter notebooks:

```python
import googlenestcam as gnc

gnc.list_cameras()                       # every Camera, with name and ID
cam = gnc.camera("Front door")           # by Google Home name or Google ID

frame = cam.snapshot()                   # slow: one Frame
frame.image, frame.time                  # NumPy RGB array, time received

with cam.stream() as s:                  # Latest mode, Audio on
    for frame in s.frames():
        model(frame.image)

with cam.stream(frames="all", audio=False) as s:   # Every-frame mode
    ...
```

Frames and Audio are read separately. `s.frames()` and `s.audio()` can each be read in their own thread at the same time. Async callers use `await cam.snapshot_async()` and `async with cam.stream_async()`.

## User Stories

1. As a developer, I want to list every Camera on my Google account, so that I know what I can stream from.
2. As a developer, I want each listed Camera to show its Google Home name and its Google ID, so that I can pick one in code.
3. As a developer, I want to pick a Camera by the name I gave it in the Google Home app, so that my code is easy to read.
4. As a developer, I want to pick a Camera by its Google ID, so that my code still works if someone renames the Camera.
5. As a developer, I want the room name used when a Camera has no custom name, so that every Camera has a usable name.
6. As a developer, I want a clear error that lists the real names when I type a wrong Camera name, so that I can fix it fast.
7. As a developer, I want a clear error that lists the IDs when two Cameras share a name, so that I can pick the right one.
8. As a developer, I want only Cameras that support WebRTC streaming in the list, so that I never pick one the package can't use.
9. As a developer, I want listing Cameras to use my saved Token without extra setup, so that it works right after Login.
10. As a developer, I want a clear error that says to run `login()` when there is no Token, so that I know the next step.
11. As a developer, I want to take one Snapshot from a Camera, so that I can grab a picture with one line.
12. As a developer, I want the docs to say a Snapshot is slow, so that I use a Stream when I need many Frames.
13. As a developer, I want a clear timeout error when a Snapshot gets no Frame, so that my program does not hang.
14. As a developer, I want the Stream behind a Snapshot always stopped, even after an error, so that I don't leave sessions open at Google.
15. As a developer, I want to open a Stream with a `with` block, so that it is always closed when I'm done.
16. As a developer, I want to loop over live Frames with a plain `for` loop, so that I can feed them to my model.
17. As a developer, I want each Frame's `.image` to be a NumPy array (height × width × 3, RGB, uint8), so that it works with PyTorch, TensorFlow and OpenCV.
18. As a developer, I want `np.asarray(frame)` to work, so that I can pass a Frame anywhere an array is expected.
19. As a developer, I want each Frame to carry `.time`, so that I can match it with Audio or log when it came.
20. As a developer doing real-time work, I want Latest mode by default, so that I always get the newest Frame even when my model is slow.
21. As a developer who must see every Frame, I want Every-frame mode (`frames="all"`), so that no Frame is skipped.
22. As a developer using Every-frame mode, I want to set the queue size, so that I control memory use.
23. As a developer using Every-frame mode, I want a clear error when the queue is full, so that I know my code is too slow.
24. As a developer using Every-frame mode, I want an option to drop the oldest Frame instead, with a warning and a drop count, so that long runs keep going.
25. As a developer, I want a Stream to keep going past Google's 5-minute limit, so that I can run for hours.
26. As a developer, I want a Stream to reconnect by itself after a short Wi-Fi drop, so that my loop doesn't stop.
27. As a developer, I want to set how many times it tries to reconnect, so that I choose between waiting and failing fast.
28. As a developer, I want a clear error from my Frame loop after the last try fails, so that I can handle it.
29. As a developer, I want Audio on by default, so that I get sound without extra settings.
30. As a developer who only needs pictures, I want `audio=False`, so that I save CPU.
31. As a developer, I want Audio chunks with `.samples` (NumPy, 48,000 per second) and `.time`, so that I can pass sound to tools like Whisper.
32. As a developer, I want Audio and Frame times on the same clock, so that I can match sound to pictures.
33. As a developer, I want to read Frames and Audio at the same time from two threads, so that one loop does not block the other.
34. As a developer who never reads Audio, I want unread Audio to not fill my memory, so that leaving it on is safe.
35. As a developer, I want `frame.to_pil()`, so that I can use Pillow tools.
36. As a developer, I want `frame.to_jpeg()`, so that I can save or send a small image.
37. As a developer without Pillow, I want a clear error that says to install `googlenestcam[images]`, so that I know how to fix it.
38. As a developer using asyncio, I want `snapshot_async()` and `stream_async()`, so that I don't block my event loop.
39. As a developer using Jupyter, I want the sync API to work inside a notebook, so that I don't hit "event loop already running".
40. As a developer, I want to open Streams on two Cameras at once, so that I can watch several places.
41. As a developer, I want leaving the `with` block to stop the Stream at Google, so that I don't waste my quota.
42. As a developer, I want the package import to never fail because of an optional extra, so that the basic install always works.
43. As a new user, I want a very short Quick start notebook (Login, list Cameras, Snapshot), so that I see results in minutes.
44. As a new user, I want a live view notebook, so that I can watch a Camera inside Jupyter.
45. As an ML developer, I want a notebook that feeds Frames to PyTorch, TensorFlow and OpenCV, so that I can copy the pattern.
46. As a server user, I want a Server login notebook, so that I can log in on a machine with no browser.
47. As a developer, I want an Audio notebook that matches sound to Frames by time, so that I can build sound features.
48. As a developer, I want a notebook with several Cameras at once, so that I see how to run them together.
49. As an async developer, I want an async notebook, so that I see the async calls in use.
50. As a developer, I want `pip install googlenestcam` to not install Jupyter, OpenCV or Pillow, so that the base install stays small.
51. As a developer, I want `googlenestcam[notebooks]` to install what the notebooks need, so that they run with one install.
52. As a developer, I want the notebooks to say how to install PyTorch or TensorFlow myself, so that the huge packages are my choice.
53. As the maintainer, I want unit tests that run with no Camera and no internet, so that CI checks every PR.
54. As the maintainer, I want real-Camera tests that skip when there is no Token, so that I can check the real thing with `make test_real_cameras`.
55. As the maintainer, I want notebooks saved with no outputs, Tokens or Camera IDs, so that nothing private is committed.

## Implementation Decisions

**Public API (the one seam tests use).** Top level: `list_cameras()`, `camera(name_or_id)`, and the existing `login()`. A Camera has `.name`, `.id`, `snapshot()`, `snapshot_async()`, `stream()`, `stream_async()`. A Stream has `frames()`, `audio()` and `dropped`. `list_cameras()` and `camera()` also take the existing auth options (Credentials, `token_path`, `on_missing_token`) and an advanced `transport=` keyword (an httpx transport). Normal users never set `transport`; tests use it to put in a fake Google.

**Background event loop (ADR 0002).** One background thread owns one event loop for the whole package. It starts on first use. Sync calls send work to it and wait. Async calls run on the caller's loop. Several Streams share the one background loop. This is built in the Camera list ticket, because `list_cameras()` is the first sync call that needs it.

**SDM client.** A small module that talks to Google's Smart Device Management API with httpx and the existing `GoogleAuth`: list devices in the project, and run a device command (`executeCommand`). Errors from Google become package errors with Google's message, not raw httpx errors.

**Camera list.** Keep devices whose live stream trait lists WebRTC as a supported protocol. Others (RTSP-only, thermostats) are left out. The name is the custom name from the device info trait. If that is empty, use the room name from the parent relations. `camera()` matches the Google ID (short form or full `enterprises/.../devices/...` form) first, then the name.

**Stream (copied from `video-stream`).** Reuse these parts of the `video-stream` streaming code, as functions, not whole files:
- The offer builder: receive-only audio then video, then a data channel; Opus audio; H.264 with profile-level-id `42e01f`; no ICE servers; offer checked for the audio, video, application order and a trailing newline.
- The answer fix: Google sends `a=candidate: ` with a blank foundation that aiortc can't parse; rewrite it to a named foundation.
- The extend loop: call `ExtendWebRtcStream` 60 seconds before `expiresAt`, and keep the new `mediaSessionId`.
- The close order: cancel the track tasks, call `StopWebRtcStream` (errors ignored), then close the peer connection.
- Treat the peer `connectionstatechange` to `failed` as a drop.

**Frame.** A small frozen object: `.image` (NumPy, H × W × 3, RGB, uint8) and `.time` (a timezone-aware UTC datetime for when it was received). It supports `np.asarray(frame)`. Decode with the `av` frame's own `to_ndarray(format="rgb24")`, so the base install needs no Pillow. Decoding runs off the event loop thread.

**Latest mode and Every-frame mode.** `stream(frames="latest" | "all", queue_size=..., on_full="raise" | "drop_oldest")`. Both use one `FrameBuffer` built on `collections.deque(maxlen=...)`. Latest mode is a deque of one Frame that each new Frame replaces. Every-frame mode is a deque of `queue_size` Frames. When full: `"raise"` (default) makes the next `frames()` read raise a clear error; `"drop_oldest"` drops, warns once, and counts in `s.dropped`.

**Reconnect.** `stream(retries=N)` with a small default. On a drop, start a new WebRTC session for the same Camera and carry on feeding the same `frames()`. After N failed tries in a row, the error is raised from `frames()` (and `audio()`). A successful reconnect resets the count.

**Snapshot.** Open a Stream with `audio=False`, wait for the first Frame with a timeout, always close it. Docstring and design doc say it is slow.

**Audio.** `stream(audio=True)` is the default. Audio chunks are small frozen objects: `.samples` (NumPy, 48 kHz) and `.time` (same clock as Frame time). Unread Audio is kept in a bounded buffer of the last few seconds; the oldest chunks are dropped so leaving Audio on never fills memory. With `audio=False` the audio track is still in the offer (Google needs it) but its packets are thrown away without decoding.

**Reading Frames and Audio together.** `frames()` and `audio()` are separate. Each can be read in its own thread at the same time. The design doc sketch is fixed to show this (today it shows two loops one after the other, and the second never runs).

**Frame helpers.** `frame.to_pil()` and `frame.to_jpeg(quality=...)`. Pillow is imported only inside them. If it is missing, raise a clear error naming `googlenestcam[images]`.

**Install extras.** Base: `httpx`, `aiortc` (brings `av`), `numpy`. `[onepassword]` (exists). `[images]`: Pillow. `[notebooks]`: Jupyter, OpenCV, Matplotlib, and Pillow. PyTorch and TensorFlow are in no extra.

**Errors.** New errors subclass `GoogleNestCamError`: one for Camera not found or name clash, one for Stream failures (Google refused, gave up reconnecting, queue full), and a timeout for Snapshot.

## Testing Decisions

- A good test calls the public API like a developer would and checks what comes out: Cameras, Frames, Audio chunks, errors. It does not check inner classes, task names or call order.
- **One seam: Google at the HTTP layer.** Tests pass a fake httpx transport, the same way the login and auth tests already use `httpx.MockTransport`. The fake Google answers device list calls with JSON. For `GenerateWebRtcStream` it starts a small local aiortc peer that answers the offer and sends made-up video (and sound) over localhost. So the real offer, answer fix, decode and buffering code all run in unit tests. The fake answer uses a blank candidate foundation, so the answer fix is tested too.
- The same fake Google can: return a short `expiresAt` (checks extend), drop its peer (checks reconnect), refuse to stream (checks errors), send Frames fast (checks Every-frame mode), and record `StopWebRtcStream` calls (checks clean close).
- This fake-Google test kit is built in the Stream in Latest mode ticket and reused by later tickets.
- Modules tested through the public API: Camera list, Stream, Snapshot, Audio, Frame helpers.
- Prior art: the login and auth tests (fake httpx transport, `tmp_path` Tokens, the autouse fixture that hides real settings); `test_real_login` for the `real_camera` skip pattern; the `video-stream` tests for the offer rules and the answer fix.
- `make test` runs unit tests anywhere, including CI, with no internet.
- `make test_real_cameras` runs tests marked `real_camera`. They skip when there is no Token or Credentials, and never run in CI.
- Tests are written first (TDD), as CLAUDE.md asks.
- Notebooks are checked by hand with a real Camera, and must be saved with no outputs.

## Out of Scope

- Events (motion, person, doorbell) through Google Pub/Sub. It costs money; low priority.
- Older RTSP-only Cameras.
- Sending sound to a Camera (talk-back).
- Recording to video files.
- PTZ, settings, or any camera control.
- Putting PyTorch or TensorFlow in any extra.

## Further Notes

- Login, Token search and Credentials are done (PR #2) and are not changed here, except that the new calls reuse them.
- `video-stream`'s `nest.py` does not run as it is (missing imports and a missing project path). Copy its functions, not the file.
- `video-stream` needs Python 3.13; this package is 3.12+. Check that copied code has no 3.13-only syntax.
- Build order: one small PR per ticket. After Stream in Latest mode, tickets 03 to 07 can run in parallel.
