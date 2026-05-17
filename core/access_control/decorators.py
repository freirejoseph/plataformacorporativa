from __future__ import annotations

from functools import wraps
from typing import Any, Callable


def require_role(*roles: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        wrapper.required_roles = roles  # type: ignore[attr-defined]
        return wrapper

    return decorator


def require_permission(*permissions: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        wrapper.required_permissions = permissions  # type: ignore[attr-defined]
        return wrapper

    return decorator
