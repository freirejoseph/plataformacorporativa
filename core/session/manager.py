from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import secrets


@dataclass
class SessionRecord:
    session_id: str
    usuario_id: int | None
    created_at: datetime
    expires_at: datetime | None
    metadata: dict[str, str] = field(default_factory=dict)
    revoked: bool = False


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}

    def create_session(
        self,
        usuario_id: int | None,
        ttl_minutes: int = 480,
        metadata: dict[str, str] | None = None,
    ) -> SessionRecord:
        now = datetime.utcnow()
        session = SessionRecord(
            session_id=secrets.token_urlsafe(32),
            usuario_id=usuario_id,
            created_at=now,
            expires_at=now + timedelta(minutes=ttl_minutes) if ttl_minutes > 0 else None,
            metadata=metadata or {},
        )
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> SessionRecord | None:
        session = self._sessions.get(session_id)
        if session is None or session.revoked:
            return None
        if session.expires_at is not None and session.expires_at < datetime.utcnow():
            self._sessions.pop(session_id, None)
            return None
        return session

    def revoke_session(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if session is None:
            return False
        session.revoked = True
        return True

    def cleanup_expired(self) -> int:
        removed = 0
        for session_id in list(self._sessions):
            session = self._sessions.get(session_id)
            if session is None or session.revoked:
                self._sessions.pop(session_id, None)
                removed += 1
                continue
            if session.expires_at is not None and session.expires_at < datetime.utcnow():
                self._sessions.pop(session_id, None)
                removed += 1
        return removed
