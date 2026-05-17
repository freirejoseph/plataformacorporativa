from __future__ import annotations

from dataclasses import dataclass


DENIED = "DENEGADO"
READ_ONLY = "SOLO_LECTURA"
ALLOWED = "PERMITIDO"


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    permission: str
    source: str


def can_access(
    user_permission: str | None = None,
    group_permission: str | None = None,
    role_permission: str | None = None,
    default_permission: str = DENIED,
) -> AccessDecision:
    candidates = [
        ("user", user_permission),
        ("group", group_permission),
        ("role", role_permission),
    ]
    for source, permission in candidates:
        if permission == DENIED:
            return AccessDecision(False, DENIED, source)
    for source, permission in candidates:
        if permission in {ALLOWED, READ_ONLY}:
            return AccessDecision(permission == ALLOWED, permission, source)
    return AccessDecision(default_permission == ALLOWED, default_permission, "default")
