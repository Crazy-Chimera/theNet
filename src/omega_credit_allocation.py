"""Deterministic proportional resource allocation from Ω-Credit."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math

from src.omega_credit_engine import OmegaCreditDistribution


@dataclass(frozen=True)
class OmegaCreditAllocation:
    id: str
    memory_by_contributor: tuple[tuple[str, float], ...]
    compute_by_contributor: tuple[tuple[str, float], ...]
    version: int = 1


def _validate_capacity(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite non-negative number")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0.0:
        raise ValueError(f"{name} must be a finite non-negative number")
    return normalized


def _canonical(
    memory: tuple[tuple[str, float], ...],
    compute: tuple[tuple[str, float], ...],
) -> str:
    return json.dumps(
        {
            "compute_by_contributor": compute,
            "memory_by_contributor": memory,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_omega_credit_allocation(
    distribution: OmegaCreditDistribution,
    memory_capacity: float,
    compute_capacity: float,
) -> OmegaCreditAllocation:
    """Allocate finite capacities proportionally to verified contribution shares."""
    if not isinstance(distribution, OmegaCreditDistribution):
        raise TypeError("distribution must be an OmegaCreditDistribution")

    memory = _validate_capacity("memory_capacity", memory_capacity)
    compute = _validate_capacity("compute_capacity", compute_capacity)

    memory_by_contributor = tuple(
        (contributor_id, memory * share)
        for contributor_id, _credit, share in distribution.contributions
    )
    compute_by_contributor = tuple(
        (contributor_id, compute * share)
        for contributor_id, _credit, share in distribution.contributions
    )

    identifier = sha256(
        _canonical(memory_by_contributor, compute_by_contributor).encode("utf-8")
    ).hexdigest()

    return OmegaCreditAllocation(
        id=identifier,
        memory_by_contributor=memory_by_contributor,
        compute_by_contributor=compute_by_contributor,
    )


__all__ = ["OmegaCreditAllocation", "create_omega_credit_allocation"]
