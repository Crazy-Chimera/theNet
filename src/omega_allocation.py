"""Deterministic proportional allocation from Ω-Credit signals."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from src.omega_credit import OmegaCredit


@dataclass(frozen=True)
class CreditAllocation:
    contributor_id: str
    credit: float
    allocation: float
    version: int = 1


def allocate_credit(
    credits: Iterable[OmegaCredit],
    capacity: float,
) -> tuple[CreditAllocation, ...]:
    if isinstance(capacity, bool) or not isinstance(capacity, (int, float)):
        raise ValueError("capacity must be a finite non-negative number")

    normalized_capacity = float(capacity)
    if not math.isfinite(normalized_capacity) or normalized_capacity < 0.0:
        raise ValueError("capacity must be a finite non-negative number")

    totals: dict[str, float] = {}

    for item in credits:
        if not isinstance(item, OmegaCredit):
            raise ValueError("credits must contain OmegaCredit values")
        if item.verified and item.credit > 0.0:
            totals[item.contributor_id] = (
                totals.get(item.contributor_id, 0.0) + item.credit
            )

    total_credit = sum(totals.values())
    if total_credit <= 0.0:
        return tuple(
            CreditAllocation(contributor_id, 0.0, 0.0)
            for contributor_id in sorted(totals)
        )

    return tuple(
        CreditAllocation(
            contributor_id=contributor_id,
            credit=credit,
            allocation=normalized_capacity * credit / total_credit,
        )
        for contributor_id, credit in sorted(totals.items())
    )
