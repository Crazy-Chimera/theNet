from thenet.engine import advance, build_closure
from src.gamma import create_convergence
from src.proposal import create_proposal
from src.verification import create_verification


STAMP = "2026-09-22T13:00:00Z"


def test_build_closure_constructs_full_architecture():
    closure = build_closure(
        source_subject="agent:a",
        target_subject="agent:b",
        relation_kind="observation",
        proposal_text="adopt verified relation",
        evidence="direct observation",
        expression_id="expression:1",
        created_at=STAMP,
    )

    assert closure.source.subject == "agent:a"
    assert closure.target.subject == "agent:b"
    assert closure.relation.source_id == closure.source.id
    assert closure.phi.relation_ids == (closure.relation.id,)
    assert closure.omega.from_state == closure.phi.id
    assert closure.omega2.transition_id == closure.omega.id
    assert closure.resonance.structure_id == closure.phi.id
    assert closure.gamma.resolved_id == closure.proposal.id
    assert closure.pi.convergence_id == closure.gamma.id
    assert closure.psi.meaning_id == closure.pi.id
    assert closure.theta.structure_id == closure.phi.id
    assert closure.rho.left_id == closure.source.id
    assert closure.sigma.relation_ids == (closure.relation.id,)

    assert closure.iota.phi_id == closure.phi.id
    assert closure.iota.omega_id == closure.omega.id
    assert closure.iota.omega2_id == closure.omega2.id
    assert closure.iota.resonance_id == closure.resonance.id
    assert closure.iota.gamma_id == closure.gamma.id
    assert closure.iota.pi_id == closure.pi.id
    assert closure.iota.psi_id == closure.psi.id
    assert closure.iota.theta_id == closure.theta.id
    assert closure.iota.rho_id == closure.rho.id
    assert closure.iota.sigma_id == closure.sigma.id
    assert closure.agent_state.singularity_id == closure.iota.id


def test_build_closure_is_deterministic():
    args = {
        "source_subject": "agent:a",
        "target_subject": "agent:b",
        "relation_kind": "observation",
        "proposal_text": "adopt verified relation",
        "evidence": "direct observation",
        "expression_id": "expression:1",
        "created_at": STAMP,
    }

    first = build_closure(**args)
    second = build_closure(**args)

    assert first == second


def test_advance_creates_next_immutable_agent_state():
    closure = build_closure(
        "agent:a",
        "agent:b",
        "observation",
        "adopt verified relation",
        "direct observation",
        "expression:1",
        STAMP,
    )
    proposal = create_proposal(
        closure.agent_state.id,
        closure.agent_state.id,
        "advance verified agent state",
        "2026-09-22T13:00:30Z",
    )
    verification = create_verification(
        proposal.id,
        closure.target.id,
        "verified next-state evidence",
        True,
        "2026-09-22T13:00:40Z",
    )
    convergence = create_convergence([proposal.id])

    evolved = advance(
        closure.agent_state,
        proposal,
        verification,
        convergence,
        "singularity:next",
        "2026-09-22T13:01:00Z",
    )

    assert evolved.subject_id == closure.agent_state.subject_id
    assert evolved.version == closure.agent_state.version + 1
    assert evolved.singularity_id == "singularity:next"
    assert evolved.id != closure.agent_state.id
