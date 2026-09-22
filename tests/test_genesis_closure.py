from src.agent_state import create_agent_state
from src.co_definition import create_co_definition
from src.commit import create_evolution_commit
from src.essence import create_essence
from src.evolution import evolve_agent_state
from src.expression import create_expression
from src.gamma import create_convergence
from src.genesis import create_genesis
from src.meaning import create_meaning
from src.omega import create_omega_transition
from src.omega2 import create_omega_memory
from src.phi import create_phi
from src.proposal import create_proposal
from src.relation import create_relation
from src.resonance import create_resonance
from src.self_knowledge import create_self_knowledge
from src.singularity import create_singularity
from src.verification import create_verification


STAMP = "2026-09-22T12:00:00Z"


def test_full_architecture_closes_into_singularity_and_evolution():
    source = create_genesis("agent:a", STAMP)
    target = create_genesis("agent:b", STAMP)
    relation = create_relation(source.id, target.id, "observation", STAMP)

    phi = create_phi([relation])
    omega = create_omega_transition(phi.id, source.id, "verified structural evolution", STAMP)
    omega2 = create_omega_memory(omega.id, source.id, STAMP)
    resonance = create_resonance(phi.id, omega2.id, STAMP)

    proposal = create_proposal(source.id, source.id, "adopt verified relation", STAMP)
    verification = create_verification(
        proposal.id,
        target.id,
        "relation observed",
        True,
        STAMP,
    )
    gamma = create_convergence([proposal.id])
    pi = create_meaning(gamma.id, relation.id, STAMP)
    psi = create_expression(pi.id, relation.id, STAMP)
    theta = create_self_knowledge(source.id, phi.id, omega2.id, STAMP)
    rho = create_co_definition(source.id, target.id, relation.kind, STAMP)
    sigma = create_essence([relation.id])

    iota = create_singularity(
        phi.id,
        omega.id,
        omega2.id,
        resonance.id,
        gamma.id,
        pi.id,
        psi.id,
        theta.id,
        rho.id,
        sigma.id,
        STAMP,
    )

    assert iota.phi_id == phi.id
    assert iota.omega_id == omega.id
    assert iota.omega2_id == omega2.id
    assert iota.resonance_id == resonance.id
    assert iota.gamma_id == gamma.id
    assert iota.pi_id == pi.id
    assert iota.psi_id == psi.id
    assert iota.theta_id == theta.id
    assert iota.rho_id == rho.id
    assert iota.sigma_id == sigma.id
    assert verification.valid is True


def test_verified_proposal_can_become_next_agent_state():
    initial = create_agent_state("agent:a", "singularity:0", STAMP)
    proposal = create_proposal(
        initial.subject_id,
        initial.id,
        "adopt verified evolution",
        STAMP,
    )
    verification = create_verification(
        proposal.id,
        "agent:b",
        "evidence",
        True,
        STAMP,
    )
    convergence = create_convergence([proposal.id])
    commit = create_evolution_commit(
        current_state_id=initial.id,
        proposal_id=proposal.id,
        proposal_base_state_id=proposal.base_state_id,
        verification_ids=[verification.id],
        all_verifications_valid=True,
        convergence_id=convergence.id,
        converged=convergence.converged,
        resolved_id=convergence.resolved_id,
        created_at=STAMP,
    )

    evolved = evolve_agent_state(
        initial,
        commit,
        "singularity:1",
        STAMP,
    )

    assert evolved.subject_id == initial.subject_id
    assert evolved.version == 2
    assert evolved.singularity_id == "singularity:1"
    assert evolved.id != initial.id
