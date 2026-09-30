import pytest
from dataclasses import FrozenInstanceError

from src.commit import create_evolution_commit
from src.evolution_history_root import EvolutionHistoryRoot, create_evolution_history_root


def make_commit(
    state: str = 'state-1',
    proposal: str = 'proposal-1',
    created_at: str = '2026-09-30T00:00:00Z',
):
    return create_evolution_commit(
        current_state_id=state,
        proposal_id=proposal,
        proposal_base_state_id=state,
        verification_ids=['verification-1'],
        all_verifications_valid=True,
        convergence_id='convergence-1',
        converged=True,
        resolved_id=proposal,
        created_at=created_at,
    )


def test_empty_history_has_deterministic_root():
    root = create_evolution_history_root([])

    assert isinstance(root, EvolutionHistoryRoot)
    assert root.commit_count == 0
    assert root.audit.valid is True


def test_root_is_order_independent():
    first = make_commit(state='state-a', proposal='proposal-a')
    second = make_commit(state='state-b', proposal='proposal-b')

    left = create_evolution_history_root([first, second])
    right = create_evolution_history_root([second, first])

    assert left == right


def test_changed_commit_changes_root():
    first = make_commit(created_at='2026-09-30T00:00:00Z')
    changed = make_commit(created_at='2026-09-30T00:01:00Z')

    left = create_evolution_history_root([first])
    right = create_evolution_history_root([changed])

    assert left.root_id != right.root_id


def test_initial_state_anchor_is_part_of_root():
    commit = make_commit(state='state-a')

    left = create_evolution_history_root([commit], initial_state_id='state-a')
    right = create_evolution_history_root([commit], initial_state_id='state-a')

    assert left.root_id == right.root_id
    assert left.initial_state_id == 'state-a'


def test_invalid_history_cannot_produce_root():
    commit = make_commit()
    replay = make_commit(created_at='2026-09-30T00:01:00Z')

    with pytest.raises(ValueError, match='invalid evolution history'):
        create_evolution_history_root([commit, replay])


def test_missing_initial_anchor_cannot_produce_root():
    commit = make_commit(state='state-a')

    with pytest.raises(ValueError, match='invalid evolution history'):
        create_evolution_history_root([commit], initial_state_id='state-b')


def test_generator_input_is_supported_and_not_mutated():
    first = make_commit(state='state-a')
    second = make_commit(state='state-b', proposal='proposal-b')
    records = [first, second]

    root = create_evolution_history_root((record for record in records))

    assert root.commit_count == 2
    assert records == [first, second]


def test_root_is_immutable():
    root = create_evolution_history_root([])

    with pytest.raises(FrozenInstanceError):
        root.commit_count = 99


def test_root_contains_audit_snapshot():
    commit = make_commit()
    root = create_evolution_history_root([commit])

    assert root.audit.commit_ids == (commit.id,)
    assert root.audit.valid is True


def test_same_history_repeated_is_stable():
    commits = [
        make_commit(state='state-a', proposal='proposal-a'),
        make_commit(state='state-b', proposal='proposal-b'),
    ]

    first = create_evolution_history_root(commits)
    second = create_evolution_history_root(commits)

    assert first.root_id == second.root_id