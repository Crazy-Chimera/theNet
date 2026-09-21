"""Minimal immutable Agent Ω integration state for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class AgentState:
    id: str
    subject_id: str
    singularity_id: str
    created_at: str
    version: int = 1


def _canonical(
    subject_id: str,
    singularity_id: str,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "created_at": created_at,
            "singularity_id": singularity_id,
            "subject_id": subject_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_agent_state(
    subject_id: str,
    singularity_id: str,
    created_at: str,
) -> AgentState:
    for name, value in {
        "subject_id": subject_id,
        "singularity_id": singularity_id,
        "created_at": created_at,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    identifier = sha256(
        _canonical(subject_id, singularity_id, created_at).encode("utf-8")
    ).hexdigest()

    return AgentState(
        id=identifier,
        subject_id=subject_id,
        singularity_id=singularity_id,
        created_at=created_at,
    )
