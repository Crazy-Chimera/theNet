"""Replay protection for verified collective evolution commits."""

from __future__ import annotations

from collections.abc import Iterable

from src.commit import EvolutionCommit


def ensure_not_replayed(
    candidate: EvolutionCommit,
    prior_commits: Iterable[EvolutionCommit] = (),
) -> None:
    """Reject duplicate application of a proposal to the same prior state."""
    if not isinstance(candidate, EvolutionCommit):
        raise ValueError("candidate must be EvolutionCommit")

    history = tuple(prior_commits)
    for commit in history:
        if not isinstance(commit, EvolutionCommit):
            raise ValueError("prior_commits must contain EvolutionCommit records")
        if commit.id == candidate.id:
            raise ValueError("evolution commit has already been applied")
        if (
            commit.proposal_id == candidate.proposal_id
            and commit.previous_state_id == candidate.previous_state_id
        ):
            raise ValueError("proposal has already been applied to previous state")
