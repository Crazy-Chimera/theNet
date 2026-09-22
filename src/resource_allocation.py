"""Resource-aware self-organizing allocation for theNet."""

from __future__ import annotations

from typing import Iterable

from src.omega_allocation import CreditAllocation, allocate_credit
from src.omega_credit import OmegaCredit
from src.resource_state import ResourceState


def allocate_from_resource_state(
    credits: Iterable[OmegaCredit],
    resource: ResourceState,
) -> tuple[CreditAllocation, ...]:
    if not isinstance(resource, ResourceState):
        raise TypeError("resource must be a ResourceState")

    remaining = max(resource.available - resource.used, 0.0)
    return allocate_credit(credits, remaining)
