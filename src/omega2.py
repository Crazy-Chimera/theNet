"""Minimal immutable Ω² memory primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class OmegaMemory:
    id: str
    transition_id: str
    state_id: str
    created_at: str
    version: int = 1


def _canonical(
    transition_id: str,
    state_id: str,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "created_at": created_at,
            "state_id": state_id,
            "transition_id": transition_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_omega_memory(
    transition_id: str,
    state_id: str,
    created_at: str,
) -> OmegaMemory:
    values = {
        "transition_id": transition_id,
        "state_id": state_id,
        "created_at": created_at,
    }
    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    identifier = sha256(
        _canonical(
            transition_id,
            state_id,
            created_at,
        ).encode("utf-8")
    ).hexdigest()

    return OmegaMemory(
        id=identifier,
        transition_id=transition_id,
        state_id=state_id,
        created_at=created_at,
    )
