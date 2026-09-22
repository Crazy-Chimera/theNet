"""Minimal immutable Agent Ω state transition from verified evolution."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from src.agent_state import AgentState
from src.commit import EvolutionCommit


def _canonical(
    current_state_id: str,
    commit_id: str,
    subject_id: str,
    singularity_id: str,
    created_at: str,
    version: int,
) -> str:
    return json.dumps(
        {
            "commit_id": commit_id,
            "created_at": created_at,
            "current_state_id": current_state_id,
            "singularity_id": singularity_id,
            "subject_id": subject_id,
            "version": version,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def evolve_agent_state(
    current_state: AgentState,
    commit: EvolutionCommit,
    new_singularity_id: str,
    created_at: str,
) -> AgentState:
    if not isinstance(current_state, AgentState):
        raise ValueError("current_state must be AgentState")
    if not isinstance(commit, EvolutionCommit):
        raise ValueError("commit must be EvolutionCommit")
    if not isinstance(new_singularity_id, str) or not new_singularity_id.strip():
        raise ValueError("new_singularity_id must be non-empty")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    if commit.previous_state_id != current_state.id:
        raise ValueError("commit does not target current state")

    version = current_state.version + 1
    identifier = sha256(
        _canonical(
            current_state.id,
            commit.id,
            current_state.subject_id,
            new_singularity_id,
            created_at,
            version,
        ).encode("utf-8")
    ).hexdigest()

    return AgentState(
        id=identifier,
        subject_id=current_state.subject_id,
        singularity_id=new_singularity_id,
        created_at=created_at,
        version=version,
    )
