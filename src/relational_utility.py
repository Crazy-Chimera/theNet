"""Deterministic immutable verified relational-utility signal for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
from typing import Iterable


@dataclass(frozen=True)
class RelationalUtility:
    id: str
    contributor_id: str
    value: float
    evidence_ids: tuple[str, ...]
    verified: bool
    created_at: str
    version: int = 1


def _validate_unit(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("value must be a finite number in [0, 1]")
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError("value must be a finite number in [0, 1]")
    return normalized


def _canonical(
    contributor_id: str,
    value: float,
    evidence_ids: tuple[str, ...],
    verified: bool,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "contributor_id": contributor_id,
            "created_at": created_at,
            "evidence_ids": evidence_ids,
            "value": value,
            "verified": verified,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_relational_utility(
    contributor_id: str,
    value: float,
    evidence_ids: Iterable[str],
    verified: bool,
    created_at: str,
) -> RelationalUtility:
    for name, item in {
        "contributor_id": contributor_id,
        "created_at": created_at,
    }.items():
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{name} must be non-empty")

    normalized_value = _validate_unit(value)

    if not isinstance(verified, bool):
        raise ValueError("verified must be boolean")

    normalized_evidence: list[str] = []
    for evidence_id in evidence_ids:
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise ValueError("evidence_ids must contain non-empty strings")
        normalized_evidence.append(evidence_id)

    canonical_evidence = tuple(sorted(set(normalized_evidence)))

    if verified and not canonical_evidence:
        raise ValueError("verified utility requires evidence_ids")

    identifier = sha256(
        _canonical(
            contributor_id,
            normalized_value,
            canonical_evidence,
            verified,
            created_at,
        ).encode("utf-8")
    ).hexdigest()

    return RelationalUtility(
        id=identifier,
        contributor_id=contributor_id,
        value=normalized_value,
        evidence_ids=canonical_evidence,
        verified=verified,
        created_at=created_at,
    )
