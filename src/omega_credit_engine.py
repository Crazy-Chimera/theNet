"""Deterministic distributed aggregation of Ω-Credit contributions."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from collections.abc import Iterable
import json
import math

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


def create_omega_credit_distribution(
    credits: Iterable[OmegaCredit],
) -> OmegaCreditDistribution:
    items = tuple(credits)

    if any(not isinstance(item, OmegaCredit) for item in items):
        raise TypeError("credits must contain only OmegaCredit objects")

    contributors = [item.contributor_id for item in items]
    if len(contributors) != len(set(contributors)):
        raise ValueError("each contributor may appear only once")

    total = sum(item.credit for item in items)
    if not math.isfinite(total) or total < 0.0:
        raise ValueError("total credit must be finite and non-negative")

    ordered = sorted(items, key=lambda item: item.contributor_id)
    if total > 0.0:
        contributions = tuple(
            (item.contributor_id, item.credit, item.credit / total)
            for item in ordered
        )
    else:
        contributions = tuple(
            (item.contributor_id, item.credit, 0.0)
            for item in ordered
        )

    identifier = sha256(
        _canonical(total, contributions).encode("utf-8")
    ).hexdigest()

    return OmegaCreditDistribution(
        id=identifier,
        total_credit=total,
        contributions=contributions,
    )


__all__ = [
    "OmegaCreditDistribution",
    "create_omega_credit_distribution",
]
