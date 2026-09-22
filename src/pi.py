"""Minimal deterministic meaning/contribution primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class Meaning:
    id: str
    convergence_id: str
    contribution_id: str
    created_at: str
    version: int = 1


def _canonical(
    convergence_id: str,
    contribution_id: str,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "contribution_id": contribution_id,
            "convergence_id": convergence_id,
            "created_at": created_at,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_meaning(
    convergence_id: str,
    contribution_id: str,
    created_at: str,
) -> Meaning:
    values = {
        "convergence_id": convergence_id,
        "contribution_id": contribution_id,
        "created_at": created_at,
    }
    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    identifier = sha256(
        _canonical(convergence_id, contribution_id, created_at).encode("utf-8")
    ).hexdigest()

    return Meaning(
        id=identifier,
        convergence_id=convergence_id,
        contribution_id=contribution_id,
        created_at=created_at,
    )


__all__ = ["Meaning", "create_meaning"]
