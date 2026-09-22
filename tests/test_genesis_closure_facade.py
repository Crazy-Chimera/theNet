from src.closure import create_genesis_closure
from src.essence import create_essence
from src.expression import create_expression
from src.gamma import create_convergence
from src.genesis import create_genesis
from src.meaning import create_meaning
from src.omega import create_omega_transition
from src.omega2 import create_omega_memory
from src.phi import create_phi
from src.relation import create_relation
from src.resonance import create_resonance
from src.self_knowledge import create_self_knowledge
from src.singularity import create_singularity
from src.co_definition import create_co_definition


STAMP = "2026-09-22T12:00:00Z"


def test_genesis_closure_accepts_matching_components():
    source = create_genesis("agent:a", STAMP)
    target = create_genesis("agent:b", STAMP)
    relation = create_relation(source.id, target.id, "observation", STAMP)

    phi = create_phi([relation])
    omega = create_omega_transition(phi.id, source.id, "verified structural evolution", STAMP)
    omega2 = create_omega_memory(omega.id, source.id, STAMP)
    resonance = create_resonance(phi.id, omega2.id, STAMP)
    gamma = create_convergence(["proposal:1"])
    pi = create_meaning(gamma.id, relation.id, STAMP)
    psi = create_expression(pi.id, relation.id, STAMP)
    theta = create_self_knowledge(source.id, phi.id, omega2.id, STAMP)
    rho = create_co_definition(source.id, target.id, relation.kind, STAMP)
    sigma = create_essence([relation.id])
    iota = create_singularity(
        phi.id, omega.id, omega2.id, resonance.id, gamma.id,
        pi.id, psi.id, theta.id, rho.id, sigma.id, STAMP,
    )

    closure = create_genesis_closure(
        phi, omega, omega2, resonance, gamma, pi, psi, theta, rho, sigma, iota
    )

    assert closure.iota.id == iota.id
    assert closure.phi.id == phi.id
    assert closure.sigma.id == sigma.id


def test_genesis_closure_rejects_mismatched_singularity():
    source = create_genesis("agent:a", STAMP)
    target = create_genesis("agent:b", STAMP)
    relation = create_relation(source.id, target.id, "observation", STAMP)
    phi = create_phi([relation])
    omega = create_omega_transition(phi.id, source.id, "change", STAMP)
    omega2 = create_omega_memory(omega.id, source.id, STAMP)
    resonance = create_resonance(phi.id, omega2.id, STAMP)
    gamma = create_convergence(["proposal:1"])
    pi = create_meaning(gamma.id, relation.id, STAMP)
    psi = create_expression(pi.id, relation.id, STAMP)
    theta = create_self_knowledge(source.id, phi.id, omega2.id, STAMP)
    rho = create_co_definition(source.id, target.id, relation.kind, STAMP)
    sigma = create_essence([relation.id])
    wrong_iota = create_singularity(
        "wrong", omega.id, omega2.id, resonance.id, gamma.id,
        pi.id, psi.id, theta.id, rho.id, sigma.id, STAMP,
    )

    import pytest
    with pytest.raises(ValueError):
        create_genesis_closure(
            phi, omega, omega2, resonance, gamma, pi, psi, theta, rho, sigma, wrong_iota
        )
