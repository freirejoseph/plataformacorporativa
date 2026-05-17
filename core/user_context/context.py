from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class UserContext:
    usuario_id: int | None = None
    usuario: str = ""
    rol: str = ""
    grupo: str = ""
    portal_origen: str = ""
    modulo_origen: str = ""
    extra: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, mapping: dict[str, object]) -> "UserContext":
        return cls(
            usuario_id=mapping.get("usuario_id"),
            usuario=str(mapping.get("usuario", "")),
            rol=str(mapping.get("rol", "")),
            grupo=str(mapping.get("grupo", "")),
            portal_origen=str(mapping.get("portal_origen", "")),
            modulo_origen=str(mapping.get("modulo_origen", "")),
            extra={k: str(v) for k, v in mapping.items() if k not in {
                "usuario_id",
                "usuario",
                "rol",
                "grupo",
                "portal_origen",
                "modulo_origen",
            }},
        )
