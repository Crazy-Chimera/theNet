"""Minimal immutable verified evolution commit for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable


@dataclass(frozen=True)
class EvolutionCommit:
    id: str
    previous_state_id: str
    proposal_id: str
    verification_ids: tuple[str, ...]
    convergence_id: str
    created_at: str
    version: int = 1


def _canonical(
    previous_state_id: str,
    proposal_id: str,
    verification_ids: tuple[str, ...],
    convergence_id: str,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "convergence_id": convergence_id,
            "created_at": created_at,
            "previous_state_id": previous_state_id,
            "proposal_id": proposal_id,
            "verification_ids": verification_ids,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_evolution_commit(
    current_state_id: str,
    proposal_id: str,
    proposal_base_state_id: str,
    verification_ids: Iterable[str],
    all_verifications_valid: bool,
    convergence_id: str,
    converged: bool,
    resolved_id: str | None,
    created_at: str,
) -> EvolutionCommit:
    values = {
        "current_state_id": current_state_id,
        "proposal_id": proposal_id,
        "proposal_base_state_id": proposal_base_state_id,
        "convergence_id": convergence_id,
        "created_at": created_at,
    }
    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    if not isinstance(all_verifications_valid, bool):
        raise ValueError("all_verifications_valid must be boolean")
    if not isinstance(converged, bool):
        raise ValueError("converged must be boolean")
    if resolved_id is not None and not isinstance(resolved_id, str):
        raise ValueError("resolved_id must be a string or None")

    normalized_verifications = []
    for verification_id in verification_ids:
        if not isinstance(verification_id, str) or not verification_id.strip():
            raise ValueError("verification_ids must contain non-empty strings")
        normalized_verifications.append(verification_id)

    canonical_verifications = tuple(sorted(set(normalized_verifications)))
    if not canonical_verifications:
        raise ValueError("verification_ids must be non-empty")

    if current_state_id != proposal_base_state_id:
        raise ValueError("proposal does not target current state")
    if not all_verifications_valid:
        raise ValueError("all verifications must be valid")
    if not converged:
        raise ValueError("proposal has not converged")
    if resolved_id != proposal_id:
        raise ValueError("convergence resolves to a different proposal")

    identifier = sha256(
        _canonical(
            current_state_id,
            proposal_id,
            canonical_verifications,
            convergence_id,
            created_at,
        ).encode("utf-8")
    ).hexdigest()

    return EvolutionCommit(
        id=identifier,
        previous_state_id=current_state_id,
        proposal_id=proposal_id,
        verification_ids=canonical_verifications,
        convergence_id=convergence_id,
        created_at=created_at,
    )
