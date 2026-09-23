import pytest

from src.commit import create_evolution_commit
from src.evolution_guard import ensure_not_replayed


def _commit(
    state: str = "state-1",
    proposal: str = "proposal-1",
    created_at: str = "2026-09-23T00:00:00Z",
):
    return create_evolution_commit(
        current_state_id=state,
        proposal_id=proposal,
        proposal_base_state_id=state,
        verification_ids=["verification-1"],
        all_verifications_valid=True,
        convergence_id="convergence-1",
        converged=True,
        resolved_id=proposal,
        created_at=created_at,
    )


def test_new_commit_is_allowed():
    ensure_not_replayed(_commit(), [])


def test_same_commit_id_is_rejected():
    commit = _commit()
    with pytest.raises(ValueError, match="already been applied"):
        ensure_not_replayed(commit, [commit])


def test_same_proposal_and_previous_state_is_rejected():
    previous = _commit(created_at="2026-09-23T00:00:00Z")
    candidate = _commit(created_at="2026-09-23T00:01:00Z")

    with pytest.raises(ValueError, match="already been applied"):
        ensure_not_replayed(candidate, [previous])


def test_same_proposal_on_new_state_is_allowed():
    previous = _commit(state="state-1")
    candidate = _commit(state="state-2")

    ensure_not_replayed(candidate, [previous])


def test_different_proposal_on_same_state_is_allowed():
    previous = _commit(proposal="proposal-1")
    candidate = _commit(proposal="proposal-2")

    ensure_not_replayed(candidate, [previous])


def test_invalid_history_record_is_rejected():
    with pytest.raises(ValueError, match="EvolutionCommit"):
        ensure_not_replayed(_commit(), [object()])
