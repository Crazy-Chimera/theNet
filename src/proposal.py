"""Minimal immutable proposal primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class Proposal:
    id: str
    proposer_id: str
    base_state_id: str
    proposal: str
    created_at: str
    version: int = 1


def _canonical(
    proposer_id: str,
    base_state_id: str,
    proposal: str,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "base_state_id": base_state_id,
            "created_at": created_at,
            "proposal": proposal,
            "proposer_id": proposer_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_proposal(
    proposer_id: str,
    base_state_id: str,
    proposal: str,
    created_at: str,
) -> Proposal:
    for name, value in {
        "proposer_id": proposer_id,
        "base_state_id": base_state_id,
        "proposal": proposal,
        "created_at": created_at,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    identifier = sha256(
        _canonical(
            proposer_id,
            base_state_id,
            proposal,
            created_at,
        ).encode("utf-8")
    ).hexdigest()

    return Proposal(
        id=identifier,
        proposer_id=proposer_id,
        base_state_id=base_state_id,
        proposal=proposal,
        created_at=created_at,
    )
