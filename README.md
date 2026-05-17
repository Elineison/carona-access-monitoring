# Carona Access Monitoring

Public case study for camera-based carona/tailgating access monitoring.

This repository models a sanitized version of an access-monitoring workflow where a camera observes a gate, groups detections into short access sessions, counts objects crossing configured zones, and opens an operator event when the number of objects does not match the expected access rule.

## Operational Problem

In access-control operations, the relevant event is often not a single detection. It is a short sequence: one gate opening, one vehicle or person expected, then another person, motorcycle, bicycle, or vehicle entering in the same access window. The system needs session logic, ROI/detection zones, cooldown discipline, and a clear event payload for operators.

## What This Demonstrates

- FastAPI API for a camera-based access-monitoring module.
- Session grouping with `session_gap_s` and `session_max_s` concepts.
- Object-class handling for person, car, motorcycle, bicycle, truck, and bus.
- Detection zone and forbidden zone configuration with normalized points.
- Public-safe event payload for possible carona/tailgating access.

## Architecture

```text
camera detections -> short access session -> object count rule -> operator event
                                  -> camera runtime -> health endpoint
```

This public version starts at the object-detection boundary. The production-style system would connect the same logic to VMS frames, object detection, tracking, WebSocket alerts, and operator screens.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8012
```

Open:

- `http://127.0.0.1:8012/`
- `http://127.0.0.1:8012/api/carona/cameras`
- `http://127.0.0.1:8012/api/carona/runtime`

Create a synthetic event:

```bash
curl -X POST http://127.0.0.1:8012/api/demo/carona-access
curl http://127.0.0.1:8012/api/carona/events
```

## Public-Safe Scope

All sites, camera IDs, events, zones, and detections are synthetic. No customer data, private IPs, gate recordings, credentials, vendor SDK files, or production alert payloads are included.

## Skills Represented

Python, FastAPI, access-control domain modeling, session logic, video analytics event design, VMS operations, and public-safe portfolio engineering.
