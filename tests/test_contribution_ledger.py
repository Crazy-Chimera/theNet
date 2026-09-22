from __future__ import annotations

import pytest

from src.contribution_ledger import (
    ContributionLedger,
    create_contribution_ledger,
)
from src.omega_credit import create_omega_credit


STAMP = "2026-09-22T17:30:00Z"


def _credit(contributor: str, utility: float) -> object:
    return create_omega_credit(
        contributor_id=contributor,
        relational_utility=utility,
        resource_efficiency=1.0,
        coherence=1.0,
        verified=True,
        created_at=STAMP,
    )


def test_ledger_accumulates_multiple_records_per_contributor():
    first = _credit("agent-a", 0.4)
    second = _credit("agent-a", 0.3)
    third = _credit("agent-b", 0.2)

    ledger = create_contribution_ledger([third, first, second])

    assert ledger.totals == (("agent-a", 0.7), ("agent-b", 0.2))
    assert ledger.entries == tuple(sorted((first.id, second.id, third.id)))


def test_ledger_is_order_independent():
    first = _credit("agent-a", 0.4)
    second = _credit("agent-b", 0.3)

    left = create_contribution_ledger([first, second])
    right = create_contribution_ledger([second, first])

    assert left.id == right.id


def test_ledger_rejects_duplicate_record():
    record = _credit("agent-a", 0.4)

    with pytest.raises(ValueError, match="only once"):
        create_contribution_ledger([record, record])


def test_ledger_rejects_non_credit_entries():
    with pytest.raises(TypeError, match="OmegaCredit"):
        create_contribution_ledger(["not-credit"])


def test_ledger_is_immutable():
    record = _credit("agent-a", 0.4)
    ledger = create_contribution_ledger([record])

    assert isinstance(ledger, ContributionLedger)
    with pytest.raises((AttributeError, TypeError)):
        ledger.totals = ()


def test_empty_ledger_is_valid_and_deterministic():
    first = create_contribution_ledger([])
    second = create_contribution_ledger([])

    assert first.id == second.id
    assert first.entries == ()
    assert first.totals == ()
