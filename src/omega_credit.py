"""Deterministic immutable Ω-Credit contribution primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math

from src.relational_utility import RelationalUtility


@dataclass(frozen=True)
class OmegaCredit:
    id: str
    contributor_id: str
    relational_utility: float
    resource_efficiency: float
    coherence: float
    verified: bool
    credit: float
    created_at: str
    version: int = 1


def _validate_unit(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number in [0, 1]")
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{name} must be a finite number in [0, 1]")
    return normalized


def _canonical(
    contributor_id: str,
    relational_utility: float,
    resource_efficiency: float,
    coherence: float,
    verified: bool,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "coherence": coherence,
            "contributor_id": contributor_id,
            "created_at": created_at,
            "relational_utility": relational_utility,
            "resource_efficiency": resource_efficiency,
            "verified": verified,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_omega_credit(
    contributor_id: str,
    relational_utility: float,
    resource_efficiency: float,
    coherence: float,
    verified: bool,
    created_at: str,
) -> OmegaCredit:
    for name, value in {
        "contributor_id": contributor_id,
        "created_at": created_at,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    utility = _validate_unit("relational_utility", relational_utility)
    efficiency = _validate_unit("resource_efficiency", resource_efficiency)
    structural_coherence = _validate_unit("coherence", coherence)

    if not isinstance(verified, bool):
        raise ValueError("verified must be boolean")

    credit = (
        utility * efficiency * structural_coherence
        if verified
        else 0.0
    )

    identifier = sha256(
        _canonical(
            contributor_id,
            utility,
            efficiency,
            structural_coherence,
            verified,
            created_at,
        ).encode("utf-8")
    ).hexdigest()

    return OmegaCredit(
        id=identifier,
        contributor_id=contributor_id,
        relational_utility=utility,
        resource_efficiency=efficiency,
        coherence=structural_coherence,
        verified=verified,
        credit=credit,
        created_at=created_at,
    )


def create_omega_credit_from_utility(
    utility: RelationalUtility,
    resource_efficiency: float,
    coherence: float,
    created_at: str,
) -> OmegaCredit:
    """Build credit from an already assessed utility signal.

    Verification stays attached to the utility record so callers cannot
    accidentally replace a verified assessment with a different flag.
    """
    if not isinstance(utility, RelationalUtility):
        raise TypeError("utility must be a RelationalUtility")

    return create_omega_credit(
        contributor_id=utility.contributor_id,
        relational_utility=utility.value,
        resource_efficiency=resource_efficiency,
        coherence=coherence,
        verified=utility.verified,
        created_at=created_at,
    )
