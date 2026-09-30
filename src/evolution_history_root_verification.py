"""Verification of an evolution-history root against supplied history."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from src.commit import EvolutionCommit
from src.evolution_history_root import EvolutionHistoryRoot, create_evolution_history_root


@dataclass(frozen=True)
class EvolutionHistoryRootVerification:
    valid: bool
    expected_root_id: str | None
    provided_root_id: str | None
    error: str | None
    version: int = 1


def verify_evolution_history_root(
    commits: Iterable[EvolutionCommit],
    root: EvolutionHistoryRoot,
    initial_state_id: str | None = None,
) -> EvolutionHistoryRootVerification:
    if not isinstance(root, EvolutionHistoryRoot):
        raise ValueError('root must be an EvolutionHistoryRoot')

    try:
        expected = create_evolution_history_root(
            commits, initial_state_id=initial_state_id
        )
    except ValueError as exc:
        return EvolutionHistoryRootVerification(
            valid=False,
            expected_root_id=None,
            provided_root_id=root.root_id,
            error=str(exc),
        )

    valid = expected.root_id == root.root_id
    return EvolutionHistoryRootVerification(
        valid=valid,
        expected_root_id=expected.root_id,
        provided_root_id=root.root_id,
        error=None if valid else 'root does not match supplied history',
    )