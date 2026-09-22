"""Narrow Φ-to-Ω-Credit integration boundary."""

from __future__ import annotations

from src.omega_credit import OmegaCredit, create_omega_credit_from_utility
from src.phi_coherence import phi_coherence
from src.relational_utility import RelationalUtility
from src.structure import PhiStructure


def create_omega_credit_from_phi(
    utility: RelationalUtility,
    resource_efficiency: float,
    structure: PhiStructure,
    created_at: str,
) -> OmegaCredit:
    if not isinstance(utility, RelationalUtility):
        raise TypeError("utility must be a RelationalUtility")
    if not isinstance(structure, PhiStructure):
        raise TypeError("structure must be a PhiStructure")

    coherence = phi_coherence(structure)
    return create_omega_credit_from_utility(
        utility=utility,
        resource_efficiency=resource_efficiency,
        coherence=coherence,
        created_at=created_at,
    )
