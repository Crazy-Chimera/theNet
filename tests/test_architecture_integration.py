from src.agent_state import create_agent_state
from src.essence import create_essence
from src.expression import create_expression
from src.gamma import create_convergence
from src.genesis import create_genesis
from src.iota import create_singularity
from src.memory import create_memory
from src.meaning import create_meaning
from src.omega import create_omega_transition
from src.phi import create_phi_structure
from src.proposal import create_proposal
from src.relation import create_relation
from src.resonance import create_resonance
from src.rho import create_rho
from src.self_knowledge import create_self_knowledge
from src.sigma import create_essence as create_sigma


STAMP = "2026-09-22T00:00:00Z"


def test_architecture_integrates_genesis_to_agent_state():
    alice = create_genesis("alice", STAMP)
    bob = create_genesis("bob", STAMP)

    relation = create_relation(alice.id, bob.id, "collaborates", STAMP)
    phi = create_phi_structure([relation])
    omega = create_omega_transition(alice.id, bob.id, "verified transition", STAMP)
    memory = create_memory(alice.id, omega.id, "transition", STAMP)
    resonance = create_resonance(phi.id, memory.id, STAMP)

    proposal = create_proposal(
        alice.id, phi.id, "retain the verified relation", STAMP
    )
    convergence = create_convergence([proposal.id])
    meaning = create_meaning(convergence.id, relation.id, STAMP)
    expression = create_expression(meaning.id, "relation-commit", STAMP)
    theta = create_self_knowledge(alice.id, phi.id, memory.id, STAMP)
    rho = create_rho(alice.id, bob.id, "co-definition", STAMP)
    sigma = create_sigma([relation.id])

    iota = create_singularity(
        phi.id,
        omega.id,
        memory.id,
        resonance.id,
        convergence.id,
        meaning.id,
        expression.id,
        theta.id,
        rho.id,
        sigma.id,
        STAMP,
    )
    agent = create_agent_state(alice.id, iota.id, STAMP)

    assert agent.subject_id == alice.id
    assert agent.singularity_id == iota.id
    assert iota.phi_id == phi.id
    assert iota.omega2_id == memory.id
    assert iota.gamma_id == convergence.id
    assert iota.pi_id == meaning.id
    assert iota.psi_id == expression.id
    assert iota.theta_id == theta.id
    assert iota.rho_id == rho.id
    assert iota.sigma_id == sigma.id


def test_architecture_is_deterministic_for_same_inputs():
    a = create_genesis("alice", STAMP)
    b = create_genesis("bob", STAMP)
    relation = create_relation(a.id, b.id, "collaborates", STAMP)
    phi = create_phi_structure([relation])
    sigma = create_essence([relation.id])

    assert phi.id == create_phi_structure([relation]).id
    assert sigma.id == create_essence([relation.id]).id
