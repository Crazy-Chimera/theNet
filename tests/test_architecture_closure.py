from dataclasses import FrozenInstanceError

import pytest

from src.closure import create_genesis_closure
from src.co_definition import create_co_definition
from src.essence import create_essence
from src.expression import create_expression
from src.gamma import create_convergence
from src.genesis import create_genesis
from src.meaning import create_meaning
from src.omega import create_omega_transition
from src.omega2 import create_omega_memory
from src.phi import create_phi_structure
from src.relation import create_relation
from src.resonance import create_resonance
from src.self_knowledge import create_self_knowledge
from src.singularity import create_singularity


STAMP = "2026-09-22T10:00:00Z"


def build_closure():
    first = create_genesis("agent-a", STAMP)
    second = create_genesis("agent-b", STAMP)
    relation = create_relation(first.id, second.id, "co-define", STAMP)
    phi = create_phi_structure([relation])
    omega = create_omega_transition(phi.id, "state:1", "verified movement", STAMP)
    omega2 = create_omega_memory(omega.id, "state:1", STAMP)
    resonance = create_resonance(phi.id, omega2.id, STAMP)
    gamma = create_convergence([omega.id])
    meaning = create_meaning(gamma.id, relation.id, STAMP)
    expression = create_expression(meaning.id, "expression:1", STAMP)
    theta_left = create_self_knowledge(first.id, phi.id, omega2.id, STAMP)
    theta_right = create_self_knowledge(second.id, phi.id, omega2.id, STAMP)
    rho = create_co_definition(theta_left.id, theta_right.id, "co-define", STAMP)
    sigma = create_essence([relation.id])
    iota = create_singularity(
        phi.id,
        omega.id,
        omega2.id,
        resonance.id,
        gamma.id,
        meaning.id,
        expression.id,
        theta_left.id,
        rho.id,
        sigma.id,
        STAMP,
    )
    closure = create_genesis_closure(
        phi,
        omega,
        omega2,
        resonance,
        gamma,
        meaning,
        expression,
        theta_left,
        rho,
        sigma,
        iota,
    )
    return closure


def test_complete_foundational_path_preserves_identity_references():
    closure = build_closure()

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


def test_complete_foundational_path_is_deterministic():
    first = build_closure()
    second = build_closure()

    assert first == second
    assert first.iota.id == second.iota.id


def test_closure_rejects_mismatched_iota():
    closure = build_closure()
    mismatched = create_singularity(
        closure.phi.id,
        closure.omega.id,
        closure.omega2.id,
        closure.resonance.id,
        closure.gamma.id,
        closure.pi.id,
        closure.psi.id,
        closure.theta.id,
        "wrong-rho",
        closure.sigma.id,
        STAMP,
    )

    with pytest.raises(ValueError, match="iota"):
        create_genesis_closure(
            closure.phi,
            closure.omega,
            closure.omega2,
            closure.resonance,
            closure.gamma,
            closure.pi,
            closure.psi,
            closure.theta,
            closure.rho,
            closure.sigma,
            mismatched,
        )


def test_closure_is_immutable():
    closure = build_closure()

    with pytest.raises(FrozenInstanceError):
        closure.phi = None
