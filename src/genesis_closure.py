"""Immutable integration boundary for theNet Genesis Closure."""

from __future__ import annotations

from dataclasses import dataclass

from src.co_definition import RelationalCoDefinition
from src.essence import Essence
from src.expression import Expression
from src.gamma import Convergence
from src.meaning import Meaning
from src.omega import OmegaTransition
from src.omega2 import OmegaMemory
from src.phi import PhiStructure
from src.resonance import Resonance
from src.self_knowledge import SelfKnowledge
from src.singularity import Singularity


@dataclass(frozen=True)
class GenesisClosure:
    phi: PhiStructure
    omega: OmegaTransition
    omega2: OmegaMemory
    resonance: Resonance
    gamma: Convergence
    pi: Meaning
    psi: Expression
    theta: SelfKnowledge
    rho: CoDefinition
    sigma: Essence
    iota: Singularity


def create_genesis_closure(
    phi: PhiStructure,
    omega: OmegaTransition,
    omega2: OmegaMemory,
    resonance: Resonance,
    gamma: Convergence,
    pi: Meaning,
    psi: Expression,
    theta: SelfKnowledge,
    rho: RelationalCoDefinition,
    sigma: Essence,
    iota: Singularity,
) -> GenesisClosure:
    components = {
        "phi": phi,
        "omega": omega,
        "omega2": omega2,
        "resonance": resonance,
        "gamma": gamma,
        "pi": pi,
        "psi": psi,
        "theta": theta,
        "rho": rho,
        "sigma": sigma,
    }

    for name, value in components.items():
        if value is None:
            raise ValueError(f"{name} must be provided")

    expected = {
        "phi_id": phi.id,
        "omega_id": omega.id,
        "omega2_id": omega2.id,
        "resonance_id": resonance.id,
        "gamma_id": gamma.id,
        "pi_id": pi.id,
        "psi_id": psi.id,
        "theta_id": theta.id,
        "rho_id": rho.id,
        "sigma_id": sigma.id,
    }

    if any(getattr(iota, name) != value for name, value in expected.items()):
        raise ValueError("iota does not reference the supplied closure components")

    return GenesisClosure(iota=iota, **components)


__all__ = ["GenesisClosure", "create_genesis_closure"]
