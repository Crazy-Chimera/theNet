"""Explicit quorum-based collective consensus for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable

from src.verification import Verification


@dataclass(frozen=True)
class Consensus:
    id: str
    proposal_id: str
    verification_ids: tuple[str, ...]
    verifier_ids: tuple[str, ...]
    quorum: int
    reached: bool
    version: int = 1


def strict_majority_quorum(eligible_verifiers: int) -> int:
    """Return the smallest quorum that is strictly greater than half."""
    if (
        not isinstance(eligible_verifiers, int)
        or isinstance(eligible_verifiers, bool)
        or eligible_verifiers < 1
    ):
        raise ValueError("eligible_verifiers must be a positive integer")
    return eligible_verifiers // 2 + 1


def _canonical(
    proposal_id: str,
    verification_ids: tuple[str, ...],
    verifier_ids: tuple[str, ...],
    quorum: int,
) -> str:
    return json.dumps(
        {
            "proposal_id": proposal_id,
            "quorum": quorum,
            "verification_ids": verification_ids,
            "verifier_ids": verifier_ids,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_consensus(
    proposal_id: str,
    verifications: Iterable[Verification],
    quorum: int,
) -> Consensus:
    if not isinstance(proposal_id, str) or not proposal_id.strip():
        raise ValueError("proposal_id must be non-empty")
    if not isinstance(quorum, int) or isinstance(quorum, bool) or quorum < 1:
        raise ValueError("quorum must be a positive integer")

    records = tuple(verifications)
    if not records:
        raise ValueError("verifications must be non-empty")

    for verification in records:
        if not isinstance(verification, Verification):
            raise ValueError("verifications must contain Verification records")
        if verification.proposal_id != proposal_id:
            raise ValueError("all verifications must target proposal_id")
        if not verification.valid:
            raise ValueError("all verifications must be valid")

    by_verifier: dict[str, Verification] = {}
    for verification in records:
        existing = by_verifier.get(verification.verifier_id)
        if existing is not None and existing.id != verification.id:
            raise ValueError("each verifier may contribute at most one verification")
        by_verifier[verification.verifier_id] = verification

    verifier_ids = tuple(sorted(by_verifier))
    verification_ids = tuple(
        sorted(verification.id for verification in by_verifier.values())
    )
    reached = len(verifier_ids) >= quorum

    identifier = sha256(
        _canonical(
            proposal_id,
            verification_ids,
            verifier_ids,
            quorum,
        ).encode("utf-8")
    ).hexdigest()

    return Consensus(
        id=identifier,
        proposal_id=proposal_id,
        verification_ids=verification_ids,
        verifier_ids=verifier_ids,
        quorum=quorum,
        reached=reached,
    )
