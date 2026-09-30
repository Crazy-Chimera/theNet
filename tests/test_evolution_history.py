import pytest
from dataclasses import FrozenInstanceError

from src.commit import create_evolution_commit
from src.evolution_history import EvolutionHistoryAudit, audit_evolution_history


def make_commit(
    state: str = "state-1",
    proposal: str = "proposal-1",
    created_at: str = "2026-09-30T00:00:00Z",
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


def test_empty_history_is_valid():
    audit = audit_evolution_history([])

    assert audit == EvolutionHistoryAudit(
        valid=True,
        commit_ids=(),
        predecessor_state_ids=(),
        branch_state_ids=(),
        error_count=0,
    )


def test_valid_history_is_deterministic_and_order_independent():
    first = make_commit(state="state-a", proposal="proposal-a")
    second = make_commit(state="state-b", proposal="proposal-b")

    left = audit_evolution_history([first, second])
    right = audit_evolution_history([second, first])

    assert left == right
    assert left.valid is True
    assert left.commit_ids == tuple(sorted((first.id, second.id)))


def test_duplicate_commit_is_invalid():
    commit = make_commit()

    audit = audit_evolution_history([commit, commit])

    assert audit.valid is False
    assert audit.error_count >= 1


def test_replayed_proposal_on_same_state_is_invalid():
    first = make_commit(created_at="2026-09-30T00:00:00Z")
    replay = make_commit(created_at="2026-09-30T00:01:00Z")

    audit = audit_evolution_history([first, replay])

    assert audit.valid is False
    assert audit.error_count >= 1


def test_distinct_proposals_from_one_state_are_reported_as_branch():
    first = make_commit(proposal="proposal-a", created_at="2026-09-30T00:00:00Z")
    second = make_commit(proposal="proposal-b", created_at="2026-09-30T00:01:00Z")

    audit = audit_evolution_history([first, second])

    assert audit.valid is True
    assert audit.branch_state_ids == ("state-1",)


def test_invalid_record_is_counted():
    audit = audit_evolution_history([object()])

    assert audit.valid is False
    assert audit.error_count == 1
    assert audit.commit_ids == ()


def test_initial_state_anchor_must_exist():
    commit = make_commit(state="state-a")

    audit = audit_evolution_history([commit], initial_state_id="state-b")

    assert audit.valid is False
    assert audit.error_count == 1


def test_initial_state_anchor_is_accepted_when_present():
    commit = make_commit(state="state-a")

    audit = audit_evolution_history([commit], initial_state_id="state-a")

    assert audit.valid is True


def test_input_is_not_mutated():
    first = make_commit(state="state-a")
    second = make_commit(state="state-b")
    records = [second, first]
    original = list(records)

    audit_evolution_history(records)

    assert records == original


def test_audit_is_immutable():
    audit = audit_evolution_history([make_commit()])

    with pytest.raises(FrozenInstanceError):
        audit.error_count = 99


def test_invalid_initial_state_argument_is_rejected():
    with pytest.raises(ValueError, match="initial_state_id"):
        audit_evolution_history([], initial_state_id="")
