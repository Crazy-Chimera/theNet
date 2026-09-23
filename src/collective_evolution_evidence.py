"""Immutable aggregation of verified Ω-Credit evolution evidence."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
import json

from src.omega_credit_evolution_receipt_binding import (
    OmegaCreditEvolutionReceiptBinding,
)


@dataclass(frozen=True)
class CollectiveEvolutionEvidence:
    id: str
    binding_ids: tuple[str, ...]
    commit_ids: tuple[str, ...]
    receipt_ids: tuple[str, ...]
    result_ids: tuple[str, ...]
    created_at: str
    version: int = 1


def _require_non_empty(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty")
    return value


def create_collective_evolution_evidence(
    bindings: Iterable[OmegaCreditEvolutionReceiptBinding],
    created_at: str,
) -> CollectiveEvolutionEvidence:
    timestamp = _require_non_empty("created_at", created_at)
    items = tuple(bindings)

    if any(
        not isinstance(binding, OmegaCreditEvolutionReceiptBinding)
        for binding in items
    ):
        raise TypeError(
            "bindings must contain only OmegaCreditEvolutionReceiptBinding objects"
        )

    unique = {binding.id: binding for binding in items}
    ordered = tuple(unique[key] for key in sorted(unique))

    binding_ids = tuple(binding.id for binding in ordered)
    commit_ids = tuple(binding.commit_id for binding in ordered)
    receipt_ids = tuple(binding.receipt_id for binding in ordered)
    result_ids = tuple(binding.result_id for binding in ordered)

    payload = {
        "binding_ids": binding_ids,
        "commit_ids": commit_ids,
        "created_at": timestamp,
        "receipt_ids": receipt_ids,
        "result_ids": result_ids,
        "version": 1,
    }
    identifier = sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return CollectiveEvolutionEvidence(
        id=identifier,
        binding_ids=binding_ids,
        commit_ids=commit_ids,
        receipt_ids=receipt_ids,
        result_ids=result_ids,
        created_at=timestamp,
    )


__all__ = [
    "CollectiveEvolutionEvidence",
    "create_collective_evolution_evidence",
]
