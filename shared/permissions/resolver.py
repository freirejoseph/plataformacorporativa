from __future__ import annotations

from dataclasses import dataclass


DENIED = "DENEGADO"
READ_ONLY = "SOLO_LECTURA"
ALLOWED = "PERMITIDO"


@dataclass(frozen=True)
class PermissionResult:
    permission: str
    source: str

    @property
    def allowed(self) -> bool:
        return self.permission == ALLOWED


def resolve_permission(
    user_permission: str | None = None,
    group_permission: str | None = None,
    role_permission: str | None = None,
    default_permission: str = DENIED,
) -> PermissionResult:
    for source, permission in (("user", user_permission), ("group", group_permission), ("role", role_permission)):
        if permission == DENIED:
            return PermissionResult(DENIED, source)
    for source, permission in (("user", user_permission), ("group", group_permission), ("role", role_permission)):
        if permission in {ALLOWED, READ_ONLY}:
            return PermissionResult(permission, source)
    return PermissionResult(default_permission, "default")
