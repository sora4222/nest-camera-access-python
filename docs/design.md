# Design

Decisions agreed for version 1. Words in **bold** are defined in [GLOSSARY.md](../GLOSSARY.md).

## Shape of the API

```python
import googlenestcam as gnc

gnc.login()  # once; opens a browser, or Server login
gnc.list_cameras()  # every Camera on the account
cam = gnc.camera("Front door")  # by Google Home name or Google ID

frame = cam.snapshot()  # slow: opens and closes a Stream
frame.image  # NumPy array, height x width x 3, RGB
frame.time

with cam.stream() as s:  # Latest mode, Audio on
    for frame in s.frames():
        ...
    for chunk in s.audio():
        chunk.samples, chunk.time  # NumPy samples at 48 kHz

with cam.stream(frames="all", audio=False) as s:  # Every-frame mode
    ...
```

Async versions: `await cam.snapshot_async()` and `async with cam.stream_async()`. See [ADR 0002](adr/0002-sync-api-over-background-event-loop.md).

## Login and Credentials

Setup steps: [login.md](login.md).


- **Credentials** come from code arguments or environment variables. 1Password is an optional extra; if it is missing or fails, the package falls back to code or environment values and only raises a clear error when nothing works. It never fails on import.
- The **Token** is saved in the user config folder (`~/.config/googlenestcam/token.json`), never the project folder. The path can be changed in code or with an environment variable.
- When no Token exists, `login()` opens a browser by default. The developer can instead ask for an error, or for **Server login**. See [ADR 0001](adr/0001-server-login-pastes-an-address.md).
- Other ways to log in a server: an SSH tunnel to the browser Login, or copying the Token (file, environment variable or 1Password).

## Streams

- **Latest mode** is the default. In **Every-frame mode**, a full queue raises a clear error by default; an option drops the oldest Frame, warns and counts drops.
- Frames have helpers to get a Pillow image or JPEG bytes.
- When the connection drops, the Stream reconnects a set number of times, then raises an error.
- Only Cameras that stream over WebRTC are supported. Older RTSP cameras are not.

## Not in version 1

Events (motion, person, doorbell) through Google Pub/Sub. Pub/Sub costs money, so it is low priority.

## Installing

| Install | Adds |
| --- | --- |
| `googlenestcam` | `aiortc`, `httpx`, `numpy` |
| `googlenestcam[onepassword]` | 1Password |
| `googlenestcam[images]` | Pillow, for image and JPEG helpers |
| `googlenestcam[notebooks]` | Jupyter, OpenCV, Matplotlib |

PyTorch and TensorFlow are in no extra; the notebook that uses them says how to install them.

## Notebooks

1. Quick start: Login, list Cameras, take a Snapshot
2. Live view inside Jupyter
3. Feeding Frames to PyTorch, TensorFlow and OpenCV
4. Server login
5. Audio
6. Several Cameras at once
7. Async use

## Testing and checks

- `make test`: unit tests with fake Google replies. Runs anywhere and in CI.
- `make test_real_cameras`: tests marked `real_camera`, skipped unless a Token and Credentials exist. Never run in CI.
- `make check`: `ruff format --check`, `ruff check`, `ty check`.
- `make build`: builds the wheel and source package into `dist/`. CI runs it too.

## Build order

One small PR per part: Login, Camera list, Stream, Snapshot, Audio, notebooks.
