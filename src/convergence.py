"""Minimal immutable Γ convergence primitive for theNet."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class Convergence:
    id: str
    candidate_states: tuple[str, ...]
    selected_state: str
    created_at: str
    version: int = 1


def _canonical(
    candidate_states: tuple[str, ...],
    selected_state: str,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "candidate_states": candidate_states,
            "created_at": created_at,
            "selected_state": selected_state,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_convergence(
    candidates: Iterable[str],
    selected_state: str,
    created_at: str,
) -> Convergence:
    items = tuple(candidates)

    if not items:
        raise ValueError("candidates must contain at least one state")
    if any(not isinstance(state, str) or not state.strip() for state in items):
        raise ValueError("candidates must contain only non-empty strings")
    if not isinstance(selected_state, str) or not selected_state.strip():
        raise ValueError("selected_state must be non-empty")

    candidate_states = tuple(sorted(set(items)))
    if selected_state not in candidate_states:
        raise ValueError("selected_state must be one of candidates")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    identifier = sha256(
        _canonical(candidate_states, selected_state, created_at).encode("utf-8")
    ).hexdigest()

    return Convergence(
        id=identifier,
        candidate_states=candidate_states,
        selected_state=selected_state,
        created_at=created_at,
    )
