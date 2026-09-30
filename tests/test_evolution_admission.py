import pytest
from dataclasses import FrozenInstanceError

from src.commit import create_evolution_commit
from src.evolution_admission import EvolutionAdmission, admit_evolution
from src.evolution_history import audit_evolution_history


STAMP = "2026-09-30T00:00:00Z"


def make_commit(
    state: str = "state-1",
    proposal: str = "proposal-1",
    convergence: str = "convergence-1",
):
    return create_evolution_commit(
        current_state_id=state,
        proposal_id=proposal,
        proposal_base_state_id=state,
        verification_ids=["verification-1"],
        all_verifications_valid=True,
        convergence_id=convergence,
        converged=True,
        resolved_id=proposal,
        created_at=STAMP,
    )


def test_matching_candidate_is_admitted():
    candidate = make_commit()
    audit = audit_evolution_history([candidate], initial_state_id="state-1")

    admission = admit_evolution(
        candidate,
        audit,
        current_state_id="state-1",
        expected_convergence_id="convergence-1",
    )

    assert admission == EvolutionAdmission(
        admissible=True,
        candidate_id=candidate.id,
        current_state_id="state-1",
        convergence_id="convergence-1",
        reason="admitted",
    )


def test_invalid_history_blocks_admission():
    candidate = make_commit()
    invalid_audit = audit_evolution_history(
        [candidate, candidate],
        initial_state_id="state-1",
    )

    admission = admit_evolution(
        candidate,
        invalid_audit,
        current_state_id="state-1",
        expected_convergence_id="convergence-1",
    )

    assert admission.admissible is False
    assert admission.reason == "history_audit_invalid"


def test_state_mismatch_blocks_admission():
    candidate = make_commit()
    audit = audit_evolution_history([candidate])

    admission = admit_evolution(
        candidate,
        audit,
        current_state_id="state-2",
        expected_convergence_id="convergence-1",
    )

    assert admission.admissible is False
    assert admission.reason == "state_mismatch"


def test_convergence_mismatch_blocks_admission():
    candidate = make_commit()
    audit = audit_evolution_history([candidate])

    admission = admit_evolution(
        candidate,
        audit,
        current_state_id="state-1",
        expected_convergence_id="convergence-2",
    )

    assert admission.admissible is False
    assert admission.reason == "convergence_mismatch"


def test_inputs_are_type_checked():
    candidate = make_commit()
    audit = audit_evolution_history([candidate])

    with pytest.raises(TypeError):
        admit_evolution(object(), audit, "state-1", "convergence-1")

    with pytest.raises(TypeError):
        admit_evolution(candidate, object(), "state-1", "convergence-1")


def test_required_context_is_non_empty():
    candidate = make_commit()
    audit = audit_evolution_history([candidate])

    with pytest.raises(ValueError):
        admit_evolution(candidate, audit, "", "convergence-1")

    with pytest.raises(ValueError):
        admit_evolution(candidate, audit, "state-1", "")


def test_admission_is_immutable():
    candidate = make_commit()
    audit = audit_evolution_history([candidate])

    admission = admit_evolution(candidate, audit, "state-1", "convergence-1")

    with pytest.raises(FrozenInstanceError):
        admission.reason = "changed"
