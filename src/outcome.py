"""Immutable measured outcome for a collective computation."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math


@dataclass(frozen=True)
class ComputationOutcome:
    id: str
    proposal_id: str
    result: str
    success: bool
    utility: float
    created_at: str
    version: int = 1


def create_computation_outcome(
    proposal_id: str,
    result: str,
    success: bool,
    utility: float,
    created_at: str,
) -> ComputationOutcome:
    for name, value in {
        "proposal_id": proposal_id,
        "result": result,
        "created_at": created_at,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    if not isinstance(success, bool):
        raise ValueError("success must be boolean")

    if isinstance(utility, bool) or not isinstance(utility, (int, float)):
        raise ValueError("utility must be a finite number in [0, 1]")
    normalized_utility = float(utility)
    if not math.isfinite(normalized_utility) or not 0.0 <= normalized_utility <= 1.0:
        raise ValueError("utility must be a finite number in [0, 1]")

    if not success and normalized_utility != 0.0:
        raise ValueError("failed outcome must have zero utility")

    canonical = json.dumps(
        {
            "created_at": created_at,
            "proposal_id": proposal_id,
            "result": result,
            "success": success,
            "utility": normalized_utility,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    identifier = sha256(canonical.encode("utf-8")).hexdigest()

    return ComputationOutcome(
        id=identifier,
        proposal_id=proposal_id,
        result=result,
        success=success,
        utility=normalized_utility,
        created_at=created_at,
    )


__all__ = ["ComputationOutcome", "create_computation_outcome"]
