from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.store import ControlPlaneStore


app = FastAPI(
    title="VMS Control Plane Demo",
    version="1.0.0",
    description="Public-safe central catalog and control-plane demo.",
)
store = ControlPlaneStore()


class AlertIn(BaseModel):
    camera_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    severity: str = Field(pattern="^(info|warning|critical)$")
    message: str = Field(min_length=1, max_length=300)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
    <main style="font-family:system-ui;max-width:900px;margin:40px auto;line-height:1.5">
      <h1>VMS Control Plane Demo</h1>
      <p>Central catalog for autonomous VMS workers, camera bindings, and alerts.</p>
      <ul>
        <li><a href="/api/topology">Topology</a></li>
        <li><a href="/api/alerts">Alerts</a></li>
        <li><a href="/api/system/health">Health</a></li>
      </ul>
    </main>
    """


@app.get("/api/topology")
def topology() -> dict:
    return store.topology()


@app.post("/api/alerts/ingest")
def ingest_alert(payload: AlertIn) -> dict:
    return store.ingest_alert(
        camera_id=payload.camera_id,
        kind=payload.kind,
        severity=payload.severity,
        message=payload.message,
    )


@app.get("/api/alerts")
def alerts() -> list[dict]:
    return store.alerts()


@app.get("/api/system/health")
def health() -> dict:
    topology_data = store.topology()
    offline = [server for server in topology_data["servers"] if server["status"] != "online"]
    return {
        "service": "vms-control-plane-demo",
        "state": "HEALTHY" if not offline else "DEGRADED",
        "servers_total": len(topology_data["servers"]),
        "cameras_total": len(topology_data["cameras"]),
        "bindings_total": len(topology_data["bindings"]),
        "issues": offline,
    }

