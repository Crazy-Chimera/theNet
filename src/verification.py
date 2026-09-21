"""Minimal immutable verification primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class Verification:
    id: str
    proposal_id: str
    verifier_id: str
    evidence: str
    valid: bool
    created_at: str
    version: int = 1


def _canonical(
    proposal_id: str,
    verifier_id: str,
    evidence: str,
    valid: bool,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "created_at": created_at,
            "evidence": evidence,
            "proposal_id": proposal_id,
            "valid": valid,
            "verifier_id": verifier_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_verification(
    proposal_id: str,
    verifier_id: str,
    evidence: str,
    valid: bool,
    created_at: str,
) -> Verification:
    for name, value in {
        "proposal_id": proposal_id,
        "verifier_id": verifier_id,
        "evidence": evidence,
        "created_at": created_at,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    if not isinstance(valid, bool):
        raise ValueError("valid must be boolean")

    identifier = sha256(
        _canonical(
            proposal_id,
            verifier_id,
            evidence,
            valid,
            created_at,
        ).encode("utf-8")
    ).hexdigest()

    return Verification(
        id=identifier,
        proposal_id=proposal_id,
        verifier_id=verifier_id,
        evidence=evidence,
        valid=valid,
        created_at=created_at,
    )
