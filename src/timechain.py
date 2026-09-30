"""Immutable Timechain branch, commit, rollback, prediction, and merge boundary."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class TimechainEvent:
    id: str
    kind: str
    state_id: str
    parent_state_id: str | None
    payload: str
    created_at: str
    version: int = 1


@dataclass(frozen=True)
class TimechainBranch:
    id: str
    name: str
    base_state_id: str
    current_state_id: str
    state_history: tuple[str, ...]
    events: tuple[TimechainEvent, ...]
    version: int = 1


@dataclass(frozen=True)
class Timechain:
    genesis_state_id: str
    branches: tuple[TimechainBranch, ...]
    version: int = 1


def create_timechain(genesis_state_id: str) -> Timechain:
    if not isinstance(genesis_state_id, str) or not genesis_state_id.strip():
        raise ValueError("genesis_state_id must be non-empty")
    return Timechain(genesis_state_id, ())


def create_branch(
    chain: Timechain,
    name: str,
    base_state_id: str | None = None,
) -> TimechainBranch:
    if not isinstance(chain, Timechain):
        raise TypeError("chain must be Timechain")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be non-empty")

    base = base_state_id or chain.genesis_state_id
    if not isinstance(base, str) or not base.strip():
        raise ValueError("base_state_id must be non-empty")
    if base != chain.genesis_state_id and not any(
        base in branch.state_history for branch in chain.branches
    ):
        raise ValueError("base_state_id is not present in chain history")

    branch_id = sha256(
        json.dumps(
            {"base_state_id": base, "name": name, "version": 1},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return TimechainBranch(branch_id, name, base, base, (base,), ())


def commit_branch(
    branch: TimechainBranch,
    state_id: str,
    payload: str,
    created_at: str,
) -> TimechainBranch:
    if not isinstance(branch, TimechainBranch):
        raise TypeError("branch must be TimechainBranch")
    for name, value in {"state_id": state_id, "payload": payload, "created_at": created_at}.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    event_id = sha256(
        json.dumps(
            {
                "kind": "COMMIT",
                "parent_state_id": branch.current_state_id,
                "payload": payload,
                "state_id": state_id,
                "created_at": created_at,
                "version": branch.version + 1,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    event = TimechainEvent(
        event_id,
        "COMMIT",
        state_id,
        branch.current_state_id,
        payload,
        created_at,
    )
    return TimechainBranch(
        branch.id,
        branch.name,
        branch.base_state_id,
        state_id,
        branch.state_history + (state_id,),
        branch.events + (event,),
        branch.version + 1,
    )


def rollback_branch(
    branch: TimechainBranch,
    state_id: str,
    created_at: str,
) -> TimechainBranch:
    if not isinstance(branch, TimechainBranch):
        raise TypeError("branch must be TimechainBranch")
    if state_id not in branch.state_history:
        raise ValueError("rollback target is not in branch history")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    event_id = sha256(
        json.dumps(
            {
                "kind": "ROLLBACK",
                "parent_state_id": branch.current_state_id,
                "state_id": state_id,
                "created_at": created_at,
                "version": branch.version + 1,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    event = TimechainEvent(
        event_id,
        "ROLLBACK",
        state_id,
        branch.current_state_id,
        "rollback",
        created_at,
    )
    return TimechainBranch(
        branch.id,
        branch.name,
        branch.base_state_id,
        state_id,
        branch.state_history,
        branch.events + (event,),
        branch.version + 1,
    )


def predict_state(
    branch: TimechainBranch,
    predicted_state_id: str,
    rationale: str,
    created_at: str,
) -> TimechainEvent:
    if not isinstance(branch, TimechainBranch):
        raise TypeError("branch must be TimechainBranch")
    for name, value in {
        "predicted_state_id": predicted_state_id,
        "rationale": rationale,
        "created_at": created_at,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    event_id = sha256(
        json.dumps(
            {
                "kind": "PREDICTION",
                "current_state_id": branch.current_state_id,
                "predicted_state_id": predicted_state_id,
                "rationale": rationale,
                "created_at": created_at,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return TimechainEvent(
        event_id,
        "PREDICTION",
        predicted_state_id,
        branch.current_state_id,
        rationale,
        created_at,
    )


def merge_branches(
    left: TimechainBranch,
    right: TimechainBranch,
    merged_state_id: str,
    created_at: str,
) -> TimechainBranch:
    if not isinstance(left, TimechainBranch) or not isinstance(right, TimechainBranch):
        raise TypeError("branches must be TimechainBranch")
    if left.base_state_id != right.base_state_id:
        raise ValueError("branches must share a base state")
    if not isinstance(merged_state_id, str) or not merged_state_id.strip():
        raise ValueError("merged_state_id must be non-empty")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    event_id = sha256(
        json.dumps(
            {
                "kind": "MERGE",
                "left": left.id,
                "right": right.id,
                "merged_state_id": merged_state_id,
                "created_at": created_at,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    event = TimechainEvent(
        event_id,
        "MERGE",
        merged_state_id,
        left.current_state_id,
        f"{left.id}:{right.id}",
        created_at,
    )
    history = tuple(dict.fromkeys(left.state_history + right.state_history + (merged_state_id,)))
    return TimechainBranch(
        event_id,
        f"{left.name}+{right.name}",
        left.base_state_id,
        merged_state_id,
        history,
        left.events + right.events + (event,),
        max(left.version, right.version) + 1,
    )


__all__ = [
    "Timechain",
    "TimechainBranch",
    "TimechainEvent",
    "commit_branch",
    "create_branch",
    "create_timechain",
    "merge_branches",
    "predict_state",
    "rollback_branch",
]
