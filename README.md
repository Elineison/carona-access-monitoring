# VMS Control Plane Demo

Public portfolio demo of a central control plane for distributed VMS workers.

This project models a real operational need: multiple autonomous video systems can keep running locally while a central application provides catalog, governance, bindings, and alert visibility.

## What This Demonstrates

- FastAPI control-plane architecture
- SQLite-backed catalog for servers, DVRs, cameras, and bindings
- worker isolation and fault-tolerant design
- alert ingestion from distributed systems
- clean operational APIs for dashboards and support teams
- public-safe modeling of a security electronics environment

## Core Idea

The central plane coordinates. Workers operate.

If the central dashboard goes offline, local video analytics and live streaming workers should continue functioning. This design reflects practical experience with production security systems where supportability and fault isolation matter.

## Run Locally

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/api/topology`
- `http://127.0.0.1:8000/api/alerts`

## Portfolio Note

All topology data is synthetic. The repository contains no production network details, private database content, customer information, or proprietary integrations.

