# googlenestcam

An installable Python package that gives developers quick access to their Google Nest Cameras, so they can feed pictures and sound into PyTorch, TensorFlow or computer vision code.

## Cameras and media

**Camera**:
A Google Nest camera or doorbell on the developer's Google account that supports live streaming over WebRTC.
_Avoid_: Device (unless meaning any Google device), cam

**Stream**:
A live connection to one Camera that delivers Frames and Audio until it is closed.
_Avoid_: Session, feed, live view

**Frame**:
One still picture taken from a Stream, as RGB pixels, with the time it was received.
_Avoid_: Image, photo, picture

**Latest mode**:
A way of reading a Stream that always gives the newest Frame and skips any the reader was too slow to take.
_Avoid_: Real-time mode, live mode

**Every-frame mode**:
A way of reading a Stream that gives every Frame in order, failing if the reader falls too far behind.
_Avoid_: Queue mode, buffered mode

**Snapshot**:
A single Frame got by briefly opening a Stream and closing it again. Slow; open a Stream when many Frames are needed.
_Avoid_: Photo, capture, still

**Audio**:
The sound received from a Camera on a Stream, delivered as Audio chunks.

**Audio chunk**:
A short run of sound samples from a Stream, with the time it was received.
_Avoid_: Packet, buffer, clip

## Access

**Credentials**:
The OAuth client ID, client secret and Device Access project ID the developer supplies, directly or through a secret manager.
_Avoid_: Secrets, keys, config

**Token**:
The saved refresh token that lets the package act on the developer's Google account without signing in again.
_Avoid_: Access token (that is short-lived and never saved), auth file

**Login**:
The one-time step where the developer approves access in Google's consent page and the Token is saved.
_Avoid_: Authorization, sign-up, setup

**Server login**:
A Login done on a machine with no browser, where the developer approves on another device and pastes the resulting address back.
_Avoid_: Headless auth, console login
