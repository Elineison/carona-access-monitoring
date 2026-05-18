from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.store import CaronaAccessMonitor


app = FastAPI(
    title='Carona Access Monitoring',
    version='2.0.0',
    description='Public case study for carona/tailgating access monitoring in camera-based security operations.',
)
monitor = CaronaAccessMonitor()


class ObjectIn(BaseModel):
    object_id: str = Field(min_length=1)
    class_name: str = Field(pattern='^(person|car|motorcycle|bicycle|truck|bus)$')
    confidence: float = Field(ge=0.0, le=1.0)
    zone: str = Field(pattern='^(approach|gate_line|inside|forbidden)$')


@app.get('/', response_class=HTMLResponse)
def index() -> str:
    return '''
    <main style="font-family:system-ui;max-width:920px;margin:40px auto;line-height:1.5">
      <p style="text-transform:uppercase;font-size:12px;letter-spacing:.08em;color:#476582">public case study</p>
      <h1>Carona Access Monitoring</h1>
      <p>
        Sanitized FastAPI service for monitoring carona/tailgating access events:
        camera zones, short access sessions, object classes, count rules and operator events.
        Dahua/Intelbras is represented as one operational platform family in this demo.
      </p>
      <ul>
        <li><a href="/api/carona/cameras">Configured cameras</a></li>
        <li><a href="/api/carona/runtime">Runtime snapshot</a></li>
        <li><a href="/api/carona/events">Events</a></li>
      </ul>
      <p>Use <code>POST /api/demo/carona-access</code> to create a synthetic access event.</p>
    </main>
    '''


@app.get('/api/carona/cameras')
def cameras() -> list[dict]:
    return monitor.cameras()


@app.get('/api/carona/runtime')
def runtime() -> dict:
    return monitor.runtime()


@app.post('/api/carona/cameras/{camera_id}/objects')
def ingest_object(camera_id: str, payload: ObjectIn) -> dict:
    if camera_id not in monitor.camera_ids():
        raise HTTPException(status_code=404, detail='Camera not found')
    return monitor.ingest_object(
        camera_id=camera_id,
        object_id=payload.object_id,
        class_name=payload.class_name,
        confidence=payload.confidence,
        zone=payload.zone,
    )


@app.post('/api/demo/carona-access')
def demo_carona_access() -> dict:
    monitor.ingest_object('gate-carona-a01', 'vehicle-104', 'car', 0.91, 'gate_line')
    monitor.ingest_object('gate-carona-a01', 'person-223', 'person', 0.86, 'inside')
    return monitor.ingest_object('gate-carona-a01', 'motorcycle-018', 'motorcycle', 0.82, 'inside')


@app.get('/api/carona/sessions')
def sessions() -> list[dict]:
    return monitor.sessions()


@app.get('/api/carona/events')
def events() -> list[dict]:
    return monitor.events()


@app.get('/api/system/health')
def health() -> dict:
    return monitor.health()
