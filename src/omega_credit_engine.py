"""Deterministic distributed aggregation of Ω-Credit contributions."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from collections.abc import Iterable
import json
import math

from src.contribution_ledger import ContributionLedger
from src.omega_credit import OmegaCredit


@dataclass(frozen=True)
class OmegaCreditDistribution:
    id: str
    total_credit: float
    contributions: tuple[tuple[str, float, float], ...]
    version: int = 1


def _canonical(
    total_credit: float,
    contributions: tuple[tuple[str, float, float], ...],
) -> str:
    return json.dumps(
        {
            "contributions": contributions,
            "total_credit": total_credit,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def _distribution_from_totals(
    totals: tuple[tuple[str, float], ...],
) -> OmegaCreditDistribution:
    total = sum(credit for _contributor_id, credit in totals)
    if not math.isfinite(total) or total < 0.0:
        raise ValueError("total credit must be finite and non-negative")

    if total > 0.0:
        contributions = tuple(
            (contributor_id, credit, credit / total)
            for contributor_id, credit in totals
        )
    else:
        contributions = tuple(
            (contributor_id, credit, 0.0)
            for contributor_id, credit in totals
        )

    identifier = sha256(
        _canonical(total, contributions).encode("utf-8")
    ).hexdigest()

    return OmegaCreditDistribution(
        id=identifier,
        total_credit=total,
        contributions=contributions,
    )


def create_omega_credit_distribution(
    credits: Iterable[OmegaCredit],
) -> OmegaCreditDistribution:
    items = tuple(credits)

    if any(not isinstance(item, OmegaCredit) for item in items):
        raise TypeError("credits must contain only OmegaCredit objects")

    contributors = [item.contributor_id for item in items]
    if len(contributors) != len(set(contributors)):
        raise ValueError("each contributor may appear only once")

    ordered = sorted(items, key=lambda item: item.contributor_id)
    return _distribution_from_totals(
        tuple((item.contributor_id, item.credit) for item in ordered)
    )


def create_omega_credit_distribution_from_ledger(
    ledger: ContributionLedger,
) -> OmegaCreditDistribution:
    """Convert persistent contributor totals into deterministic shares."""
    if not isinstance(ledger, ContributionLedger):
        raise TypeError("ledger must be a ContributionLedger")

    return _distribution_from_totals(ledger.totals)


__all__ = [
    "OmegaCreditDistribution",
    "create_omega_credit_distribution",
    "create_omega_credit_distribution_from_ledger",
]
