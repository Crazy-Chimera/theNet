from agent_state import create_agent_state
from commit import create_evolution_commit
from evolution import evolve_agent_state


def make_commit(state_id: str):
    return create_evolution_commit(
        current_state_id=state_id,
        proposal_id="proposal-1",
        proposal_base_state_id=state_id,
        verification_ids=["verification-1"],
        all_verifications_valid=True,
        convergence_id="convergence-1",
        converged=True,
        resolved_id="proposal-1",
        created_at="2026-09-22T10:00:00Z",
    )


def test_evolution_preserves_subject_and_increments_version():
    current = create_agent_state("subject-1", "unity-1", "2026-09-22T09:00:00Z")
    commit = make_commit(current.id)

    next_state = evolve_agent_state(
        current,
        commit,
        "unity-2",
        "2026-09-22T10:01:00Z",
    )

    assert next_state.subject_id == current.subject_id
    assert next_state.singularity_id == "unity-2"
    assert next_state.version == current.version + 1
    assert next_state.id != current.id


def test_evolution_is_deterministic():
    current = create_agent_state("subject-1", "unity-1", "2026-09-22T09:00:00Z")
    commit = make_commit(current.id)

    first = evolve_agent_state(current, commit, "unity-2", "2026-09-22T10:01:00Z")
    second = evolve_agent_state(current, commit, "unity-2", "2026-09-22T10:01:00Z")

    assert first.id == second.id


def test_wrong_lineage_is_rejected():
    current = create_agent_state("subject-1", "unity-1", "2026-09-22T09:00:00Z")
    other = create_agent_state("subject-2", "unity-2", "2026-09-22T09:00:00Z")
    commit = make_commit(other.id)

    try:
        evolve_agent_state(current, commit, "unity-3", "2026-09-22T10:01:00Z")
    except ValueError as exc:
        assert str(exc) == "commit does not target current state"
    else:
        raise AssertionError("expected lineage rejection")


def test_evolution_does_not_mutate_current_state():
    current = create_agent_state("subject-1", "unity-1", "2026-09-22T09:00:00Z")
    original = current
    commit = make_commit(current.id)

    evolve_agent_state(current, commit, "unity-2", "2026-09-22T10:01:00Z")

    assert current == original
