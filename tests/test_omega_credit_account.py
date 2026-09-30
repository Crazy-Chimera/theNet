from dataclasses import FrozenInstanceError

import pytest

from src.omega_credit import create_omega_credit
from src.omega_credit_account import (
    create_omega_credit_account,
    earn_omega_credit,
    spend_omega_credit,
)


STAMP = "2026-09-30T00:00:00Z"


def verified_credit(contributor: str, value: float = 0.5):
    return create_omega_credit(
        contributor,
        value,
        1.0,
        1.0,
        True,
        STAMP,
    )


def test_account_starts_at_zero():
    account = create_omega_credit_account("agent:a")
    assert account.balance == 0.0
    assert account.earned_credit_ids == ()
    assert account.spending_ids == ()


def test_verified_credit_can_be_earned():
    account = create_omega_credit_account("agent:a")
    updated = earn_omega_credit(account, verified_credit("agent:a"))

    assert updated.balance == pytest.approx(0.5)
    assert updated.earned_credit_ids
    assert updated.version == 2
    assert account.balance == 0.0


def test_credit_can_be_spent():
    account = create_omega_credit_account("agent:a")
    earned = earn_omega_credit(account, verified_credit("agent:a", 0.8))
    spent = spend_omega_credit(earned, 0.3, "compute")

    assert spent.balance == pytest.approx(0.5)
    assert len(spent.spending_ids) == 1
    assert earned.balance == pytest.approx(0.8)


def test_overspending_is_rejected():
    account = create_omega_credit_account("agent:a")
    with pytest.raises(ValueError, match="insufficient"):
        spend_omega_credit(account, 0.1, "compute")


def test_unverified_credit_cannot_be_earned():
    account = create_omega_credit_account("agent:a")
    credit = create_omega_credit("agent:a", 1.0, 1.0, 1.0, False, STAMP)

    with pytest.raises(ValueError, match="verified"):
        earn_omega_credit(account, credit)


def test_duplicate_earning_is_rejected():
    account = create_omega_credit_account("agent:a")
    credit = verified_credit("agent:a")
    earned = earn_omega_credit(account, credit)

    with pytest.raises(ValueError, match="already"):
        earn_omega_credit(earned, credit)


def test_wrong_contributor_is_rejected():
    account = create_omega_credit_account("agent:a")

    with pytest.raises(ValueError, match="does not match"):
        earn_omega_credit(account, verified_credit("agent:b"))


def test_account_is_immutable():
    account = create_omega_credit_account("agent:a")

    with pytest.raises(FrozenInstanceError):
        account.balance = 1.0
