from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Dict, List


@dataclass
class AccessSession:
    id: str
    camera_id: str
    started_at: float
    last_seen_at: float
    objects: Dict[str, dict] = field(default_factory=dict)
    event_sent: bool = False

    def payload(self) -> dict:
        return {
            'id': self.id,
            'camera_id': self.camera_id,
            'started_at': self.started_at,
            'last_seen_at': self.last_seen_at,
            'elapsed_s': round(self.last_seen_at - self.started_at, 2),
            'object_count': len(self.objects),
            'objects': list(self.objects.values()),
            'event_sent': self.event_sent,
        }


class CaronaAccessMonitor:
    def __init__(self) -> None:
        self._cameras = [
            {
                'id': 'gate-carona-a01',
                'name': 'Portão de acesso de veículos',
                'site': 'Acesso residencial A',
                'platform_family': 'intelbras',
                'analysis_fps': 4.0,
                'session_gap_s': 2.5,
                'session_max_s': 15.0,
                'allowed_objects_per_session': 1,
                'roi': [
                    {'x': 0.18, 'y': 0.18},
                    {'x': 0.84, 'y': 0.16},
                    {'x': 0.86, 'y': 0.88},
                    {'x': 0.20, 'y': 0.92},
                ],
                'detection_zone': [
                    {'x': 0.32, 'y': 0.34},
                    {'x': 0.74, 'y': 0.34},
                    {'x': 0.78, 'y': 0.82},
                    {'x': 0.28, 'y': 0.84},
                ],
                'forbidden_zone': [
                    {'x': 0.00, 'y': 0.62},
                    {'x': 0.26, 'y': 0.62},
                    {'x': 0.26, 'y': 1.00},
                    {'x': 0.00, 'y': 1.00},
                ],
            },
            {
                'id': 'gate-carona-b02',
                'name': 'Portão de pedestres e motos',
                'site': 'Acesso residencial B',
                'platform_family': 'intelbras',
                'analysis_fps': 4.0,
                'session_gap_s': 2.0,
                'session_max_s': 12.0,
                'allowed_objects_per_session': 1,
                'roi': [
                    {'x': 0.22, 'y': 0.20},
                    {'x': 0.78, 'y': 0.20},
                    {'x': 0.80, 'y': 0.90},
                    {'x': 0.20, 'y': 0.90},
                ],
                'detection_zone': [],
                'forbidden_zone': [],
            },
        ]
        self._sessions: List[AccessSession] = []
        self._events: List[dict] = []

    def camera_ids(self) -> set[str]:
        return {camera['id'] for camera in self._cameras}

    def cameras(self) -> list[dict]:
        return [
            {
                **camera,
                'runtime': self._runtime_for(camera['id']),
            }
            for camera in self._cameras
        ]

    def runtime(self) -> dict:
        active_sessions = [session.payload() for session in self._active_sessions()]
        return {
            'service': 'carona-access-monitoring',
            'state': 'RUNNING',
            'cameras_total': len(self._cameras),
            'active_sessions': active_sessions,
            'open_events': len([event for event in self._events if event['status'] == 'open']),
            'session_gap_s': {camera['id']: camera['session_gap_s'] for camera in self._cameras},
        }

    def ingest_object(self, camera_id: str, object_id: str, class_name: str, confidence: float, zone: str) -> dict:
        now = time()
        camera = self._camera(camera_id)
        session = self._current_or_new_session(camera, now)
        session.last_seen_at = now
        session.objects[object_id] = {
            'object_id': object_id,
            'class_name': class_name,
            'confidence': round(float(confidence), 3),
            'zone': zone,
            'last_seen_at': now,
        }
        event = self._maybe_create_event(camera, session, zone)
        return {'session': session.payload(), 'event': event}

    def sessions(self) -> list[dict]:
        return [session.payload() for session in self._sessions]

    def events(self) -> list[dict]:
        return list(self._events)

    def health(self) -> dict:
        runtime = self.runtime()
        return {
            'service': 'carona-access-monitoring',
            'state': 'HEALTHY',
            'cameras_total': runtime['cameras_total'],
            'active_sessions': len(runtime['active_sessions']),
            'open_events': runtime['open_events'],
            'issues': [],
        }

    def _runtime_for(self, camera_id: str) -> dict:
        sessions = [session.payload() for session in self._active_sessions() if session.camera_id == camera_id]
        return {
            'state': 'RUNNING',
            'active_sessions': sessions,
            'last_event_id': self._events[-1]['id'] if self._events else None,
        }

    def _current_or_new_session(self, camera: dict, now: float) -> AccessSession:
        active = [session for session in self._active_sessions() if session.camera_id == camera['id']]
        if active:
            return active[-1]
        session = AccessSession(
            id=f"sess-carona-{len(self._sessions) + 1:04d}",
            camera_id=camera['id'],
            started_at=now,
            last_seen_at=now,
        )
        self._sessions.append(session)
        return session

    def _active_sessions(self) -> list[AccessSession]:
        now = time()
        out = []
        for session in self._sessions:
            camera = self._camera(session.camera_id)
            if now - session.last_seen_at <= float(camera['session_gap_s']):
                out.append(session)
        return out

    def _maybe_create_event(self, camera: dict, session: AccessSession, zone: str) -> dict | None:
        object_count = len(session.objects)
        allowed = int(camera['allowed_objects_per_session'])
        if session.event_sent:
            return None
        if object_count <= allowed and zone != 'forbidden':
            return None

        session.event_sent = True
        event = {
            'id': f"evt-carona-{len(self._events) + 1:04d}",
            'type': 'possible_carona_access',
            'severity': 'warning' if zone != 'forbidden' else 'critical',
            'camera_id': camera['id'],
            'camera_name': camera['name'],
            'site': camera['site'],
            'session_id': session.id,
            'object_count': object_count,
            'allowed_objects_per_session': allowed,
            'objects': list(session.objects.values()),
            'operator_note': 'Mais objetos do que o esperado cruzaram a área de acesso na mesma sessão curta.',
            'created_at': time(),
            'status': 'open',
        }
        self._events.append(event)
        return event

    def _camera(self, camera_id: str) -> dict:
        for camera in self._cameras:
            if camera['id'] == camera_id:
                return camera
        raise KeyError(camera_id)
