# ADR-007: Camera Access via MJPEG Bridge

**Status:** Accepted
**Date:** 2024-12-29
**Deciders:** Patrick (PO), Claude (PM/Architect)

## Context

The Reachy Home Assistant requires camera access from the Reachy Mini Wireless robot for face recognition. The intelligence (face recognition, LLM inference) runs on a Jetson Orin NX, while the robot has an embedded Raspberry Pi 4.

### Technical Constraints

1. **Reachy SDK Camera Requirements:**
   - WebRTC streaming via GStreamer
   - Requires `webrtcsrc` element from `gst-plugins-rs` (Rust plugins)
   - `gst-plugins-rs` requires GStreamer 1.20+

2. **Jetson Orin NX Environment:**
   - Ships with GStreamer 1.16.3 (Ubuntu 20.04)
   - NVIDIA provides `nvidia-l4t-gstreamer` plugins built against 1.16.3
   - Upgrading GStreamer risks breaking DeepStream, NVENC/NVDEC, and other GPU-accelerated pipelines

3. **Alternative Approaches Attempted:**
   - `aiortc` (Python WebRTC): DTLS handshake failures
   - GStreamer `webrtcbin`: Promise callback issues in mixed asyncio/GLib environment
   - SDK's `GstSignallingConsumer`: Same promise failures
   - Direct OpenCV capture on RPi: Daemon has exclusive camera access

## Decision

Implement an **MJPEG HTTP bridge** that runs on the Reachy's Raspberry Pi:

1. A Python script on the RPi connects to the local daemon (where WebRTC works)
2. Captures frames via the SDK's `media.get_frame()`
3. Re-serves frames as MJPEG over HTTP on port 8081
4. Jetson consumes frames via simple HTTP requests (no GStreamer needed)

Motor control continues via the SDK with `media_backend="no_media"`.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Reachy Mini RPi                          │
│  ┌──────────────┐    ┌─────────────────┐    ┌───────────────┐  │
│  │ Reachy Daemon│───▶│ rpi_daemon_bridge│───▶│ HTTP Server   │  │
│  │ (WebRTC)     │    │ (SDK + OpenCV)   │    │ (port 8081)   │  │
│  └──────────────┘    └─────────────────┘    └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP/MJPEG
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Jetson Orin NX                             │
│  ┌─────────────────┐    ┌──────────────────┐                   │
│  │ Camera Client   │───▶│ Face Recognition │                   │
│  │ (HTTP requests) │    │ Pipeline         │                   │
│  └─────────────────┘    └──────────────────┘                   │
│           │                                                     │
│           │ SDK (motors only, no media)                        │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ ReachyMini SDK  │──────── REST API ──────▶ Reachy Motors    │
│  └─────────────────┘                                           │
└─────────────────────────────────────────────────────────────────┘
```

## Consequences

### Positive

- **No GStreamer upgrade required** — Jetson's NVIDIA pipeline intact
- **Simple HTTP protocol** — Universal compatibility, easy debugging
- **Decoupled architecture** — Camera and motor control are independent
- **Works today** — Verified functional 2024-12-29
- **Low latency** — MJPEG has no keyframe waiting (50-100ms typical)

### Negative

- **Manual startup** — Bridge script must be started after robot power-on (mitigated by future systemd service)
- **Bandwidth** — MJPEG less efficient than H.264 (~5-10 Mbps at 640x480@30fps)
- **Additional moving part** — One more service to monitor
- **Not using SDK as designed** — Workaround may break with SDK updates

### Neutral

- **Resolution trade-off** — Can adjust quality/resolution for bandwidth vs. quality
- **WiFi dependency** — Same as native SDK approach

## Alternatives Considered

### 1. Upgrade GStreamer on Jetson
- **Pros:** Use SDK as designed
- **Cons:** High risk of breaking NVIDIA pipelines; complex rebuild process
- **Decision:** Rejected — risk outweighs benefit

### 2. USB Webcam on Jetson
- **Pros:** Simple, reliable, no network dependency
- **Cons:** Doesn't use robot's camera; requires separate hardware
- **Decision:** Deferred — may still add for room-wide presence detection (different use case)

### 3. Run face recognition on RPi
- **Pros:** No network video streaming
- **Cons:** RPi 4 lacks GPU acceleration; would bottleneck the system
- **Decision:** Rejected — Jetson GPU is key asset

### 4. Contact Pollen Robotics for alternative
- **Pros:** Might get official solution
- **Cons:** Unknown timeline; may not exist
- **Decision:** Deferred — can pursue in parallel

## Implementation Files

| File | Location | Purpose |
|------|----------|---------|
| `rpi_daemon_bridge.py` | Reachy RPi: `/home/pollen/` | MJPEG server using SDK |
| `jetson_camera_client.py` | Jetson: `~/reachy-assistant/` | Frame consumer with examples |
| `rpi_camera_server.py` | Backup | Direct OpenCV (if daemon releases camera) |

## API Contract

**Base URL:** `http://<reachy-ip>:8081`

| Endpoint | Method | Response |
|----------|--------|----------|
| `/health` | GET | `{"status": "ok"}` |
| `/frame` | GET | Single JPEG image |
| `/video_feed` | GET | MJPEG stream |
| `/stats` | GET | Capture statistics JSON |

## Integration with Face Recognition

The camera client provides frames to the face recognition pipeline in `src/assistant/recognition/face.py`:

```python
# Example integration (pseudocode)
import requests
import numpy as np
from PIL import Image
from io import BytesIO

def get_frame_from_reachy():
    response = requests.get("http://10.0.0.48:8081/frame", timeout=1.0)
    image = Image.open(BytesIO(response.content))
    return np.array(image)  # RGB format for face_recognition library

# In main loop
frame = get_frame_from_reachy()
user_id, confidence = face_recognizer.recognize(frame)
```

## Future Improvements

1. **Systemd service** — Auto-start on boot
2. **Resolution endpoint** — Dynamic quality adjustment
3. **Authentication** — Basic auth (low priority on home network)
4. **Reconnection logic** — Handle daemon restarts gracefully

## References

- [Reachy Mini SDK](https://github.com/pollen-robotics/reachy-mini)
- [gst-plugins-rs](https://github.com/GStreamer/gst-plugins-rs)
- [RidgeRun: Upgrading GStreamer on Jetson](https://developer.ridgerun.com/wiki/index.php/Upgrading_GStreamer_version_of_NVIDIA_Jetson)
- Setup Tracker: `docs/jetson-setup-tracker.md`

## Related Decisions

- ADR-001: Data storage (where face encodings are stored)
- ADR-005: Speech pipeline (audio capture shares similar constraints)
- ADR-006: Deployment architecture (systemd service patterns)
