"""Read-only integrity audit for EvolutionCommit history."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from src.commit import EvolutionCommit


@dataclass(frozen=True)
class EvolutionHistoryAudit:
    valid: bool
    commit_ids: tuple[str, ...]
    predecessor_state_ids: tuple[str, ...]
    branch_state_ids: tuple[str, ...]
    error_count: int


def audit_evolution_history(
    commits: Iterable[EvolutionCommit],
    initial_state_id: str | None = None,
) -> EvolutionHistoryAudit:
    if initial_state_id is not None and (
        not isinstance(initial_state_id, str) or not initial_state_id.strip()
    ):
        raise ValueError("initial_state_id must be non-empty when supplied")

    records = tuple(commits)
    errors = 0
    valid_records: list[EvolutionCommit] = []

    for record in records:
        if not isinstance(record, EvolutionCommit):
            errors += 1
            continue
        if not record.previous_state_id.strip():
            errors += 1
            continue
        valid_records.append(record)

    ordered = tuple(sorted(valid_records, key=lambda record: record.id))

    seen_ids: set[str] = set()
    applied_pairs: set[tuple[str, str]] = set()
    proposals_by_state: dict[str, set[str]] = {}

    for record in ordered:
        if record.id in seen_ids:
            errors += 1
        else:
            seen_ids.add(record.id)

        pair = (record.proposal_id, record.previous_state_id)
        if pair in applied_pairs:
            errors += 1
        else:
            applied_pairs.add(pair)

        proposals_by_state.setdefault(record.previous_state_id, set()).add(
            record.proposal_id
        )

    if initial_state_id is not None and not any(
        record.previous_state_id == initial_state_id for record in ordered
    ):
        errors += 1

    branch_state_ids = tuple(
        sorted(
            state_id
            for state_id, proposal_ids in proposals_by_state.items()
            if len(proposal_ids) > 1
        )
    )

    commit_ids = tuple(record.id for record in ordered)
    predecessor_state_ids = tuple(
        sorted({record.previous_state_id for record in ordered})
    )

    return EvolutionHistoryAudit(
        valid=errors == 0,
        commit_ids=commit_ids,
        predecessor_state_ids=predecessor_state_ids,
        branch_state_ids=branch_state_ids,
        error_count=errors,
    )
