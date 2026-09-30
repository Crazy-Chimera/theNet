"""Deterministic immutable anchor between evolution-history roots."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class EvolutionHistoryRootAnchor:
    id: str
    previous_root_id: str | None
    current_root_id: str
    created_at: str
    version: int = 1


def _canonical(
    previous_root_id: str | None,
    current_root_id: str,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "created_at": created_at,
            "current_root_id": current_root_id,
            "previous_root_id": previous_root_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_evolution_history_root_anchor(
    current_root_id: str,
    created_at: str,
    previous_root_id: str | None = None,
) -> EvolutionHistoryRootAnchor:
    if not isinstance(current_root_id, str) or not current_root_id.strip():
        raise ValueError("current_root_id must be non-empty")

    if previous_root_id is not None and (
        not isinstance(previous_root_id, str) or not previous_root_id.strip()
    ):
        raise ValueError("previous_root_id must be non-empty when supplied")

    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    identifier = sha256(
        _canonical(
            previous_root_id,
            current_root_id,
            created_at,
        ).encode("utf-8")
    ).hexdigest()

    return EvolutionHistoryRootAnchor(
        id=identifier,
        previous_root_id=previous_root_id,
        current_root_id=current_root_id,
        created_at=created_at,
    )
