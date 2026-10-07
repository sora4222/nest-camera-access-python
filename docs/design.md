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
frame.to_pil()  # Pillow image; needs googlenestcam[images]
frame.to_jpeg(quality=85)  # JPEG bytes; needs googlenestcam[images]

with cam.stream() as s:  # Latest mode, Audio on
    for frame in s.frames():  # loops until you break or leave the block
        ...
# Audio: read s.audio() in another thread at the same time;
# each chunk has .samples (NumPy, 48 kHz) and .time.

with cam.stream(frames="all", audio=False) as s:  # Every-frame mode
    ...
```

To pass settings in code instead of environment variables, make a **Nest**:

```python
nest = gnc.Nest(token_path="token.json", on_missing_token="raise")
cam = nest.camera("Front door")
```

Async versions: `await gnc.list_cameras_async()`, `await gnc.camera_async(...)`, `await cam.snapshot_async()` and `async with cam.stream_async()`. See [ADR 0002](adr/0002-sync-api-over-background-event-loop.md).

## Login and Credentials

Setup steps: [login.md](login.md).


- **Credentials** come from code arguments or environment variables. 1Password is an optional extra; if it is missing or fails, the package falls back to code or environment values and only raises a clear error when nothing works. It never fails on import.
- The **Token** file is found in this order: a path in code, `GOOGLENESTCAM_TOKEN_PATH`, `./token.json` if it exists, then `~/.config/googlenestcam/token.json` as the last resort.
- When no Token exists, `login()` opens a browser by default. The developer can instead ask for an error, or for **Server login**. See [ADR 0001](adr/0001-server-login-pastes-an-address.md).
- Other ways to log in a server: an SSH tunnel to the browser Login, or copying the Token (file, environment variable or 1Password).

## Streams

- A Stream runs on the hidden background loop. Leaving the `with` block stops it at Google (`StopWebRtcStream`), also after an error. It is extended a minute before Google's 5-minute expiry, so it can run for hours.
- **Latest mode** is the default. In **Every-frame mode** (`cam.stream(frames="all", queue_size=100)`), a full queue raises a clear error by default; `on_full="drop_oldest"` drops the oldest Frame, warns once and counts drops in `stream.dropped`. Both modes use one buffer built on `collections.deque(maxlen=...)`: one Frame in Latest mode, `queue_size` Frames in Every-frame mode.
- Frames have helpers to get a Pillow image or JPEG bytes.
- **Frame size**: `cam.stream(size=720)` (height; width keeps the shape) or `size=(640, 360)` resizes every Frame before you get it, so later steps run faster. `snapshot()` takes `size` too. Google's API has no way to ask a Camera for a smaller video, so the package resizes. Off by default. See [the spec](../.scratch/frame-size/spec.md).
- When the connection drops, the Stream starts a new session by itself, up to `retries` times in a row (3 by default, 1 second apart). The count resets once a Frame arrives. After the last failed try, `frames()` raises `StreamError`.
- Only Cameras that stream over WebRTC are supported. Older RTSP cameras are not.

## Snapshots

- `cam.snapshot(timeout=20)` starts a Stream, waits for one Frame, then stops it, also on error or timeout. It is slow, so open a Stream when you need many Frames.
- If no Frame arrives in time, it raises `SnapshotTimeoutError`.

## Not in version 1

Events (motion, person, doorbell) through Google Pub/Sub. Pub/Sub costs money, so it is low priority.

## Installing

| Install | Adds |
| --- | --- |
| `googlenestcam` | `aiortc`, `httpx`, `numpy` |
| `googlenestcam[onepassword]` | 1Password |
| `googlenestcam[images]` | Pillow, for image and JPEG helpers |
| `googlenestcam[notebooks]` | Jupyter, OpenCV (headless), Matplotlib, Pillow |

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
