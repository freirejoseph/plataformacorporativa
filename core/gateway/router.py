from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteTarget:
    codigo: str
    nombre: str
    url: str
    componente: str | None = None


def resolve_route(routes: list[RouteTarget], codigo: str) -> RouteTarget | None:
    for route in routes:
        if route.codigo == codigo:
            return route
    return None
