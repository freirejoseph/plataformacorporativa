from __future__ import annotations

from dataclasses import dataclass, field
from collections import defaultdict


@dataclass(frozen=True)
class MenuItem:
    id: int
    codigo: str
    nombre: str
    menu_padre_id: int | None = None
    icono: str | None = None
    orden: int = 0
    estado: str = "ACTIVO"
    extra: dict[str, str] = field(default_factory=dict)


def build_menu_tree(items: list[MenuItem]) -> list[dict[str, object]]:
    children: dict[int | None, list[MenuItem]] = defaultdict(list)
    for item in items:
        children[item.menu_padre_id].append(item)
    for bucket in children.values():
        bucket.sort(key=lambda item: (item.orden, item.id))

    def serialize(item: MenuItem) -> dict[str, object]:
        return {
            "id": item.id,
            "codigo": item.codigo,
            "nombre": item.nombre,
            "icono": item.icono,
            "orden": item.orden,
            "estado": item.estado,
            "children": [serialize(child) for child in children.get(item.id, [])],
        }

    return [serialize(item) for item in children.get(None, [])]


def filter_menu_items(items: list[MenuItem], allowed_codes: set[str]) -> list[MenuItem]:
    return [item for item in items if item.codigo in allowed_codes]
