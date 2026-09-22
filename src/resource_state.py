"""Deterministic immutable local resource state for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math


@dataclass(frozen=True)
class ResourceState:
    id: str
    available: float
    used: float
    efficiency: float
    created_at: str
    version: int = 1


def _validate_resource(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite non-negative number")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0.0:
        raise ValueError(f"{name} must be a finite non-negative number")
    return normalized


def _canonical(
    available: float,
    used: float,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "available": available,
            "created_at": created_at,
            "used": used,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_resource_state(
    available: float,
    used: float,
    created_at: str,
) -> ResourceState:
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    normalized_available = _validate_resource("available", available)
    normalized_used = _validate_resource("used", used)

    efficiency = (
        min(normalized_used / normalized_available, 1.0)
        if normalized_available > 0.0
        else 0.0
    )

    identifier = sha256(
        _canonical(
            normalized_available,
            normalized_used,
            created_at,
        ).encode("utf-8")
    ).hexdigest()

    return ResourceState(
        id=identifier,
        available=normalized_available,
        used=normalized_used,
        efficiency=efficiency,
        created_at=created_at,
    )
