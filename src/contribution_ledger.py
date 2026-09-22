"""Persistent immutable accounting of verified Ω-Credit records."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
import json
import math

from src.omega_credit import OmegaCredit


@dataclass(frozen=True)
class ContributionLedger:
    id: str
    entries: tuple[str, ...]
    totals: tuple[tuple[str, float], ...]
    version: int = 1


def _canonical(
    entries: tuple[str, ...],
    totals: tuple[tuple[str, float], ...],
) -> str:
    return json.dumps(
        {
            "entries": entries,
            "totals": totals,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_contribution_ledger(
    credits: Iterable[OmegaCredit],
) -> ContributionLedger:
    items = tuple(credits)

    if any(not isinstance(item, OmegaCredit) for item in items):
        raise TypeError("credits must contain only OmegaCredit objects")

    entry_ids = tuple(sorted(item.id for item in items))
    if len(entry_ids) != len(set(entry_ids)):
        raise ValueError("each OmegaCredit record may appear only once")

    totals_by_contributor: dict[str, float] = defaultdict(float)
    for item in items:
        totals_by_contributor[item.contributor_id] += item.credit

    totals = tuple(sorted(totals_by_contributor.items()))
    if any(not math.isfinite(total) or total < 0.0 for _, total in totals):
        raise ValueError("aggregate credit must be finite and non-negative")

    identifier = sha256(
        _canonical(entry_ids, totals).encode("utf-8")
    ).hexdigest()

    return ContributionLedger(
        id=identifier,
        entries=entry_ids,
        totals=totals,
    )


__all__ = ["ContributionLedger", "create_contribution_ledger"]
