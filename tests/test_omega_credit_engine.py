from dataclasses import FrozenInstanceError

import pytest

from src.omega_credit import create_omega_credit
from src.omega_credit_engine import (
    OmegaCreditDistribution,
    create_omega_credit_distribution,
)


STAMP = "2026-09-22T00:00:00Z"


def credit(contributor: str, value: float, verified: bool = True):
    return create_omega_credit(
        contributor_id=contributor,
        relational_utility=value,
        resource_efficiency=1.0,
        coherence=1.0,
        verified=verified,
        created_at=STAMP,
    )


def test_distribution_aggregates_and_normalizes():
    state = create_omega_credit_distribution(
        [credit("b", 0.25), credit("a", 0.75)]
    )

    assert isinstance(state, OmegaCreditDistribution)
    assert state.total_credit == pytest.approx(1.0)
    assert state.contributions == (
        ("a", 0.75, 0.75),
        ("b", 0.25, 0.25),
    )


def test_input_order_does_not_change_distribution():
    first = credit("a", 0.4)
    second = credit("b", 0.6)

    assert create_omega_credit_distribution([first, second]) == (
        create_omega_credit_distribution([second, first])
    )


def test_zero_total_produces_zero_shares():
    state = create_omega_credit_distribution(
        [credit("a", 0.0, verified=False), credit("b", 0.0, verified=False)]
    )

    assert state.total_credit == 0.0
    assert state.contributions == (
        ("a", 0.0, 0.0),
        ("b", 0.0, 0.0),
    )


def test_duplicate_contributor_is_rejected():
    with pytest.raises(ValueError):
        create_omega_credit_distribution([credit("a", 0.5), credit("a", 0.5)])


def test_invalid_item_is_rejected():
    with pytest.raises(TypeError):
        create_omega_credit_distribution([object()])


def test_distribution_is_immutable():
    state = create_omega_credit_distribution([credit("a", 1.0)])

    with pytest.raises(FrozenInstanceError):
        state.total_credit = 2.0


def test_distribution_identity_is_deterministic():
    credits = [credit("a", 0.2), credit("b", 0.8)]

    first = create_omega_credit_distribution(credits)
    second = create_omega_credit_distribution(credits)

    assert first.id == second.id
