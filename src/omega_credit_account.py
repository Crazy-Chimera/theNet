"""Immutable Ω-Credit account boundary for earning and spending credit."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math

from src.omega_credit import OmegaCredit


@dataclass(frozen=True)
class OmegaCreditAccount:
    account_id: str
    contributor_id: str
    balance: float
    earned_credit_ids: tuple[str, ...] = ()
    spending_ids: tuple[str, ...] = ()
    version: int = 1


def create_omega_credit_account(contributor_id: str) -> OmegaCreditAccount:
    if not isinstance(contributor_id, str) or not contributor_id.strip():
        raise ValueError("contributor_id must be non-empty")
    account_id = sha256(
        json.dumps(
            {"contributor_id": contributor_id, "version": 1},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return OmegaCreditAccount(account_id, contributor_id, 0.0)


def earn_omega_credit(
    account: OmegaCreditAccount,
    credit: OmegaCredit,
) -> OmegaCreditAccount:
    if not isinstance(account, OmegaCreditAccount):
        raise TypeError("account must be OmegaCreditAccount")
    if not isinstance(credit, OmegaCredit):
        raise TypeError("credit must be OmegaCredit")
    if credit.contributor_id != account.contributor_id:
        raise ValueError("credit contributor does not match account")
    if not credit.verified or credit.credit <= 0.0:
        raise ValueError("only positive verified credit can be earned")
    if credit.id in account.earned_credit_ids:
        raise ValueError("credit record has already been earned")

    return OmegaCreditAccount(
        account_id=account.account_id,
        contributor_id=account.contributor_id,
        balance=account.balance + credit.credit,
        earned_credit_ids=account.earned_credit_ids + (credit.id,),
        spending_ids=account.spending_ids,
        version=account.version + 1,
    )


def spend_omega_credit(
    account: OmegaCreditAccount,
    amount: float,
    reason: str,
) -> OmegaCreditAccount:
    if not isinstance(account, OmegaCreditAccount):
        raise TypeError("account must be OmegaCreditAccount")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError("amount must be positive and finite")
    if not math.isfinite(float(amount)) or amount <= 0.0:
        raise ValueError("amount must be positive")
    if amount > account.balance:
        raise ValueError("insufficient credit")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("reason must be non-empty")

    spend_id = sha256(
        json.dumps(
            {
                "account_id": account.account_id,
                "amount": float(amount),
                "reason": reason,
                "version": account.version + 1,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    return OmegaCreditAccount(
        account_id=account.account_id,
        contributor_id=account.contributor_id,
        balance=account.balance - float(amount),
        earned_credit_ids=account.earned_credit_ids,
        spending_ids=account.spending_ids + (spend_id,),
        version=account.version + 1,
    )


__all__ = [
    "OmegaCreditAccount",
    "create_omega_credit_account",
    "earn_omega_credit",
    "spend_omega_credit",
]
