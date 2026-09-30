"""Deterministic root for an audited evolution history."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from collections.abc import Iterable

from src.commit import EvolutionCommit
from src.evolution_history import EvolutionHistoryAudit, audit_evolution_history


@dataclass(frozen=True)
class EvolutionHistoryRoot:
    root_id: str
    commit_count: int
    initial_state_id: str | None
    audit: EvolutionHistoryAudit
    version: int = 1


def _canonical(audit: EvolutionHistoryAudit, initial_state_id: str | None) -> str:
    return json.dumps(
        {
            "branch_state_ids": audit.branch_state_ids,
            "commit_ids": audit.commit_ids,
            "initial_state_id": initial_state_id,
            "predecessor_state_ids": audit.predecessor_state_ids,
            "version": 1,
        },
        sort_keys=True,
        separators=(',', ':'),
    )


def create_evolution_history_root(
    commits: Iterable[EvolutionCommit],
    initial_state_id: str | None = None,
) -> EvolutionHistoryRoot:
    audit = audit_evolution_history(commits, initial_state_id=initial_state_id)
    if not audit.valid:
        raise ValueError("cannot create root from invalid evolution history")

    root_id = sha256(
        _canonical(audit, initial_state_id).encode('utf-8')
    ).hexdigest()

    return EvolutionHistoryRoot(
        root_id=root_id,
        commit_count=len(audit.commit_ids),
        initial_state_id=initial_state_id,
        audit=audit,
    )