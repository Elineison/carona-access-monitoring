from __future__ import annotations

import sqlite3
from pathlib import Path
from time import time
from typing import Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS servers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    status TEXT NOT NULL,
    base_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cameras (
    id TEXT PRIMARY KEY,
    site TEXT NOT NULL,
    name TEXT NOT NULL,
    vendor TEXT NOT NULL,
    channel INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS bindings (
    camera_id TEXT PRIMARY KEY,
    live_server_id TEXT NOT NULL,
    analytics_server_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    camera_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at REAL NOT NULL
);
"""


SEED_SERVERS = [
    ("srv-live-01", "Live Gateway Worker", "live", "online", "http://demo-live.local"),
    ("srv-analytics-01", "Analytics Worker A", "analytics", "online", "http://demo-analytics-a.local"),
    ("srv-analytics-02", "Analytics Worker B", "analytics", "online", "http://demo-analytics-b.local"),
]

SEED_CAMERAS = [
    ("cam-social-01", "Demo Tower", "Elevator Social", "generic-hikvision", 7),
    ("cam-service-01", "Demo Tower", "Elevator Service", "generic-intelbras", 8),
    ("cam-lobby-01", "Demo Plaza", "Lobby", "generic-dahua", 3),
]

SEED_BINDINGS = [
    ("cam-social-01", "srv-live-01", "srv-analytics-01"),
    ("cam-service-01", "srv-live-01", "srv-analytics-02"),
    ("cam-lobby-01", "srv-live-01", "srv-analytics-01"),
]


class ControlPlaneStore:
    def __init__(self, db_path: str = "control_plane_demo.db") -> None:
        self.db_path = Path(db_path)
        self._init()

    def topology(self) -> dict:
        return {
            "servers": self._select("SELECT * FROM servers ORDER BY id"),
            "cameras": self._select("SELECT * FROM cameras ORDER BY id"),
            "bindings": self._select("SELECT * FROM bindings ORDER BY camera_id"),
        }

    def ingest_alert(self, camera_id: str, kind: str, severity: str, message: str) -> dict:
        alert = {
            "id": f"alert-{int(time() * 1000)}",
            "camera_id": camera_id,
            "kind": kind,
            "severity": severity,
            "message": message,
            "created_at": time(),
        }
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO alerts (id, camera_id, kind, severity, message, created_at)
                VALUES (:id, :camera_id, :kind, :severity, :message, :created_at)
                """,
                alert,
            )
        return alert

    def alerts(self) -> list[dict]:
        return self._select("SELECT * FROM alerts ORDER BY created_at DESC")

    def _init(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            self._seed(conn, "servers", SEED_SERVERS)
            self._seed(conn, "cameras", SEED_CAMERAS)
            self._seed(conn, "bindings", SEED_BINDINGS)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _seed(conn: sqlite3.Connection, table: str, rows: Iterable[tuple]) -> None:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        if count:
            return
        placeholders = ",".join(["?"] * len(next(iter(rows))))
        conn.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)

    def _select(self, sql: str) -> list[dict]:
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(sql).fetchall()]

