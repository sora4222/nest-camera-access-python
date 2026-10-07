# Spec: Frame size (smaller Frames for faster downstream code)

Status: ready-for-agent

Words in **bold** are from `GLOSSARY.md`.

## Problem Statement

A developer feeding **Frames** into a model or OpenCV often wants small pictures, for example 640 x 360, so their code runs faster. Today every Frame comes at the full size the **Camera** sends, and the developer must resize each one themselves.

## Research: can Google send a smaller size?

No. Checked in Google's Device Access docs on 2026-10-07:

- The [CameraLiveStream trait](https://developers.google.com/nest/device-access/traits/device/camera-live-stream) has `maxVideoResolution` (the most the Camera can send). It is read-only; nothing lets a client pick a size.
- `GenerateWebRtcStream` takes only `offerSdp`. `ExtendWebRtcStream` takes only `mediaSessionId`. Neither has a size, bitrate or quality setting.
- The docs list rules for the SDP offer (Opus audio, media order and so on) but say nothing about the offer changing the video size.
- The [supported devices page](https://developers.google.com/nest/device-access/supported-devices) lists no sizes and no way to choose one.

WebRTC has general hints a receiver can put in its offer (`b=AS` bandwidth, H.264 `max-fs`). Google does not document them for Nest, so the package does not rely on them. They could be tried later against a real Camera.

## Solution

The package resizes each Frame before the developer gets it:

```python
with cam.stream(size=(640, 360)) as s:
    for frame in s.frames():
        frame.image.shape  # (360, 640, 3)

with cam.stream(size=720) as s:  # height 720, width keeps the shape
    ...

frame = cam.snapshot(size=(320, 180))
```

- `size=` on `stream()`, `stream_async()`, `snapshot()` and `snapshot_async()`.
- A single number such as `480`, `720` or `1080` is the height. The width keeps the picture's shape, like "720p". Added at Jesse's request on PR #10.
- Off by default (`size=None`): Frames keep the Camera's size.
- `(width, height)` stretches the picture to exactly that size. The developer picks a size with the same shape as the Camera (most Nest Cameras are 16:9) to avoid stretching.
- Resizing is done by PyAV (already installed with aiortc) while it turns the video into RGB, in one step, off the event loop. No new dependency.

## User Stories

1. As a developer, I want to ask for smaller Frames, so that my model or OpenCV code runs faster.
2. As a developer, I want the same option on Snapshots, so that a single picture is small too.
3. As a developer, I want Frames at full size when I don't ask, so that nothing changes for existing code.
4. As a developer, I want a clear error for a bad size, so that I find my mistake before the Stream starts.

## Implementation Decisions

- The decoder turns each video frame into RGB with `to_ndarray(width=..., height=..., format="rgb24")` when a size is set. For a single number, the width is worked out from each frame's own shape.
- The size is passed from `Camera` to the Stream or Snapshot, then to each WebRTC session, so reconnects keep it.
- A size must be one whole number, or two, each at least 1. Otherwise `ValueError` is raised when `stream()` or `snapshot()` is called.

## Testing Decisions

- Through the public API, against the fake Google: a Stream and a Snapshot with `size` give Frames of that shape and still red; a single number gives that height with the shape kept; with no `size`, Frames keep the fake Camera's size; a bad size raises `ValueError`.

## Out of Scope

- Asking Google for a smaller stream (not possible today, see Research).
- Cropping.
