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
One still picture taken from a Stream, as RGB pixels.
_Avoid_: Image, photo, picture

**Snapshot**:
A single Frame got by briefly opening a Stream and closing it again. Slow; open a Stream when many Frames are needed.
_Avoid_: Photo, capture, still

**Audio**:
The sound received from a Camera on a Stream.

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
