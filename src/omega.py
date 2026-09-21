"""Minimal immutable Ω state-transition primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class OmegaTransition:
    id: str
    from_state: str
    to_state: str
    reason: str
    created_at: str
    version: int = 1


def _canonical(
    from_state: str,
    to_state: str,
    reason: str,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "created_at": created_at,
            "from_state": from_state,
            "reason": reason,
            "to_state": to_state,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_omega_transition(
    from_state: str,
    to_state: str,
    reason: str,
    created_at: str,
) -> OmegaTransition:
    values = {
        "from_state": from_state,
        "to_state": to_state,
        "reason": reason,
        "created_at": created_at,
    }
    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    identifier = sha256(
        _canonical(
            from_state,
            to_state,
            reason,
            created_at,
        ).encode("utf-8")
    ).hexdigest()

    return OmegaTransition(
        id=identifier,
        from_state=from_state,
        to_state=to_state,
        reason=reason,
        created_at=created_at,
    )
