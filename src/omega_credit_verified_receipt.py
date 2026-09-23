"""Deterministic receipt for a verified Ω-Credit execution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from hashlib import sha256
import json
import math

from src.omega_credit_conservation import audit_omega_credit_conservation
from src.omega_credit_distributed_engine import OmegaCreditEngineResult


@dataclass(frozen=True)
class OmegaCreditVerifiedReceipt:
    id: str
    result_id: str
    audit_valid: bool
    memory_before_used: float
    compute_before_used: float
    memory_capacity: float
    compute_capacity: float
    version: int = 1


def _canonical(value: object) -> str:
    if not is_dataclass(value):
        raise TypeError("value must be a dataclass")
    return json.dumps(
        asdict(value),
        sort_keys=True,
        separators=(",", ":"),
    )


def _validate_number(name: str, value: float) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
    ):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def create_omega_credit_verified_receipt(
    result: OmegaCreditEngineResult,
    memory_before_used: float,
    compute_before_used: float,
    memory_capacity: float,
    compute_capacity: float,
) -> OmegaCreditVerifiedReceipt:
    audit = audit_omega_credit_conservation(
        result,
        memory_before_used,
        compute_before_used,
        memory_capacity,
        compute_capacity,
    )
    if not audit.valid:
        raise ValueError(f"Ω-Credit conservation audit failed: {audit.reason}")

    before_memory = _validate_number("memory_before_used", memory_before_used)
    before_compute = _validate_number("compute_before_used", compute_before_used)
    memory_limit = _validate_number("memory_capacity", memory_capacity)
    compute_limit = _validate_number("compute_capacity", compute_capacity)

    result_id = sha256(_canonical(result).encode("utf-8")).hexdigest()
    receipt_payload = {
        "compute_before_used": before_compute,
        "compute_capacity": compute_limit,
        "memory_before_used": before_memory,
        "memory_capacity": memory_limit,
        "result_id": result_id,
        "version": 1,
    }
    receipt_id = sha256(
        json.dumps(
            receipt_payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    return OmegaCreditVerifiedReceipt(
        id=receipt_id,
        result_id=result_id,
        audit_valid=True,
        memory_before_used=before_memory,
        compute_before_used=before_compute,
        memory_capacity=memory_limit,
        compute_capacity=compute_limit,
    )


__all__ = [
    "OmegaCreditVerifiedReceipt",
    "create_omega_credit_verified_receipt",
]
