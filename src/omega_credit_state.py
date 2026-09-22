"""Compose verified utility, local resource state, and Φ coherence into Ω-Credit."""

from __future__ import annotations

from src.omega_credit import OmegaCredit, create_omega_credit
from src.phi_coherence import phi_coherence
from src.relational_utility import RelationalUtility
from src.resource_state import ResourceState
from src.structure import PhiStructure


def create_omega_credit_from_state(
    utility: RelationalUtility,
    resource: ResourceState,
    structure: PhiStructure,
    created_at: str,
) -> OmegaCredit:
    """Derive the bounded Ω-Credit inputs from canonical state objects."""
    if not isinstance(utility, RelationalUtility):
        raise TypeError("utility must be a RelationalUtility")
    if not isinstance(resource, ResourceState):
        raise TypeError("resource must be a ResourceState")
    if not isinstance(structure, PhiStructure):
        raise TypeError("structure must be a PhiStructure")

    if resource.available > 0.0:
        remaining = max(resource.available - resource.used, 0.0)
        resource_efficiency = remaining / resource.available
    else:
        resource_efficiency = 0.0

    return create_omega_credit(
        contributor_id=utility.contributor_id,
        relational_utility=utility.value,
        resource_efficiency=resource_efficiency,
        coherence=phi_coherence(structure),
        verified=utility.verified,
        created_at=created_at,
    )


__all__ = ["create_omega_credit_from_state"]
