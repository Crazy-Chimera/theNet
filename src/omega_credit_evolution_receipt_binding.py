"""Immutable binding between an EvolutionCommit and verified Ω-Credit receipt."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from src.commit import EvolutionCommit
from src.omega_credit_verified_receipt import OmegaCreditVerifiedReceipt


@dataclass(frozen=True)
class OmegaCreditEvolutionReceiptBinding:
    id: str
    commit_id: str
    receipt_id: str
    result_id: str
    created_at: str
    version: int = 1


def _require_non_empty(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty")
    return value


def create_omega_credit_evolution_receipt_binding(
    commit: EvolutionCommit,
    receipt: OmegaCreditVerifiedReceipt,
    created_at: str,
) -> OmegaCreditEvolutionReceiptBinding:
    if not isinstance(commit, EvolutionCommit):
        raise TypeError("commit must be an EvolutionCommit")
    if not isinstance(receipt, OmegaCreditVerifiedReceipt):
        raise TypeError("receipt must be an OmegaCreditVerifiedReceipt")
    if receipt.audit_valid is not True:
        raise ValueError("receipt must be audit-valid")

    commit_id = _require_non_empty("commit.id", commit.id)
    receipt_id = _require_non_empty("receipt.id", receipt.id)
    result_id = _require_non_empty("receipt.result_id", receipt.result_id)
    timestamp = _require_non_empty("created_at", created_at)

    payload = {
        "commit_id": commit_id,
        "created_at": timestamp,
        "receipt_id": receipt_id,
        "result_id": result_id,
        "version": 1,
    }
    identifier = sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return OmegaCreditEvolutionReceiptBinding(
        id=identifier,
        commit_id=commit_id,
        receipt_id=receipt_id,
        result_id=result_id,
        created_at=timestamp,
    )


__all__ = [
    "OmegaCreditEvolutionReceiptBinding",
    "create_omega_credit_evolution_receipt_binding",
]
