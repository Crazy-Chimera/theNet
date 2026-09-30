import pytest
from dataclasses import FrozenInstanceError

from src.commit import create_evolution_commit
from src.evolution_history_root import create_evolution_history_root
from src.evolution_history_root_verification import (
    EvolutionHistoryRootVerification,
    verify_evolution_history_root,
)


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


def test_matching_root_is_valid():
    commits = [make_commit()]
    root = create_evolution_history_root(commits)

    result = verify_evolution_history_root(commits, root)

    assert isinstance(result, EvolutionHistoryRootVerification)
    assert result.valid is True
    assert result.expected_root_id == root.root_id
    assert result.provided_root_id == root.root_id
    assert result.error is None


def test_changed_history_is_invalid():
    original = [make_commit(created_at='2026-09-30T00:00:00Z')]
    root = create_evolution_history_root(original)
    changed = [make_commit(created_at='2026-09-30T00:01:00Z')]

    result = verify_evolution_history_root(changed, root)

    assert result.valid is False
    assert result.error == 'root does not match supplied history'


def test_changed_initial_anchor_is_invalid():
    commits = [make_commit(state='state-a')]
    root = create_evolution_history_root(commits, initial_state_id='state-a')

    result = verify_evolution_history_root(
        commits, root, initial_state_id='state-b'
    )

    assert result.valid is False
    assert result.expected_root_id is None
    assert 'invalid evolution history' in result.error


def test_invalid_history_is_never_accepted():
    commit = make_commit()
    replay = make_commit(created_at='2026-09-30T00:01:00Z')
    root = create_evolution_history_root([commit])

    result = verify_evolution_history_root([commit, replay], root)

    assert result.valid is False
    assert result.expected_root_id is None


def test_wrong_root_type_is_rejected():
    with pytest.raises(ValueError, match='EvolutionHistoryRoot'):
        verify_evolution_history_root([], object())


def test_verification_is_deterministic():
    commits = [
        make_commit(state='state-a', proposal='proposal-a'),
        make_commit(state='state-b', proposal='proposal-b'),
    ]
    root = create_evolution_history_root(commits)

    left = verify_evolution_history_root(commits, root)
    right = verify_evolution_history_root(list(reversed(commits)), root)

    assert left == right


def test_input_is_not_mutated():
    commits = [make_commit()]
    original = list(commits)
    root = create_evolution_history_root(commits)

    verify_evolution_history_root(commits, root)

    assert commits == original


def test_result_is_immutable():
    commits = [make_commit()]
    root = create_evolution_history_root(commits)
    result = verify_evolution_history_root(commits, root)

    with pytest.raises(FrozenInstanceError):
        result.valid = False


def test_root_is_not_mutated():
    commits = [make_commit()]
    root = create_evolution_history_root(commits)
    before = root

    verify_evolution_history_root(commits, root)

    assert root == before