"""Pure conservation audit for the distributed Ω-Credit engine."""

from __future__ import annotations

from dataclasses import dataclass
import math

from src.omega_credit_distributed_engine import OmegaCreditEngineResult


_EPS = 1e-9


@dataclass(frozen=True)
class OmegaCreditConservationAudit:
    valid: bool
    reason: str = ""


def audit_omega_credit_conservation(
    result: OmegaCreditEngineResult,
    memory_before_used: float,
    compute_before_used: float,
    memory_capacity: float,
    compute_capacity: float,
) -> OmegaCreditConservationAudit:
    """Verify accounting and resource conservation without mutating the result."""
    if not isinstance(result, OmegaCreditEngineResult):
        raise TypeError("result must be an OmegaCreditEngineResult")

    values = (
        memory_before_used,
        compute_before_used,
        memory_capacity,
        compute_capacity,
        result.distribution.total_credit,
    )
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        for value in values
    ):
        return OmegaCreditConservationAudit(False, "non-finite numeric state")

    contributors = [item.contributor_id for item in result.credits]
    if len(contributors) != len(set(contributors)):
        return OmegaCreditConservationAudit(False, "duplicate contributor")

    credit_sum = math.fsum(item.credit for item in result.credits)
    ledger_sum = math.fsum(value for _id, value in result.ledger.totals)
    if not math.isclose(credit_sum, ledger_sum, rel_tol=_EPS, abs_tol=_EPS):
        return OmegaCreditConservationAudit(False, "ledger total mismatch")

    if not math.isclose(
        ledger_sum,
        result.distribution.total_credit,
        rel_tol=_EPS,
        abs_tol=_EPS,
    ):
        return OmegaCreditConservationAudit(False, "distribution total mismatch")

    if any(
        credit < -_EPS or share < -_EPS
        for _id, credit, share in result.distribution.contributions
    ):
        return OmegaCreditConservationAudit(False, "negative distribution value")

    shares = math.fsum(share for _id, _credit, share in result.distribution.contributions)
    expected_shares = 1.0 if result.distribution.total_credit > _EPS else 0.0
    if not math.isclose(shares, expected_shares, rel_tol=_EPS, abs_tol=_EPS):
        return OmegaCreditConservationAudit(False, "distribution shares are not normalized")

    memory_allocated = math.fsum(
        value for _id, value in result.allocation.memory_by_contributor
    )
    compute_allocated = math.fsum(
        value for _id, value in result.allocation.compute_by_contributor
    )
    if memory_allocated < -_EPS or compute_allocated < -_EPS:
        return OmegaCreditConservationAudit(False, "negative allocation")

    if memory_allocated > float(memory_capacity) + _EPS:
        return OmegaCreditConservationAudit(False, "memory allocation exceeds capacity")
    if compute_allocated > float(compute_capacity) + _EPS:
        return OmegaCreditConservationAudit(False, "compute allocation exceeds capacity")

    memory_delta = result.memory_resource.used - float(memory_before_used)
    compute_delta = result.compute_resource.used - float(compute_before_used)
    if memory_delta < -_EPS or compute_delta < -_EPS:
        return OmegaCreditConservationAudit(False, "resource usage regressed")

    if not math.isclose(memory_delta, memory_allocated, rel_tol=_EPS, abs_tol=_EPS):
        return OmegaCreditConservationAudit(False, "memory commit mismatch")
    if not math.isclose(compute_delta, compute_allocated, rel_tol=_EPS, abs_tol=_EPS):
        return OmegaCreditConservationAudit(False, "compute commit mismatch")

    if result.distribution.total_credit <= _EPS and (
        abs(memory_delta) > _EPS or abs(compute_delta) > _EPS
    ):
        return OmegaCreditConservationAudit(False, "zero credit increased resources")

    return OmegaCreditConservationAudit(True)


__all__ = ["OmegaCreditConservationAudit", "audit_omega_credit_conservation"]
