"""Minimal immutable Ψ expression association for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class Expression:
    id: str
    meaning_id: str
    expression_id: str
    created_at: str
    version: int = 1


def _canonical(
    meaning_id: str,
    expression_id: str,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "created_at": created_at,
            "expression_id": expression_id,
            "meaning_id": meaning_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_expression(
    meaning_id: str,
    expression_id: str,
    created_at: str,
) -> Expression:
    for name, value in {
        "meaning_id": meaning_id,
        "expression_id": expression_id,
        "created_at": created_at,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    identifier = sha256(
        _canonical(meaning_id, expression_id, created_at).encode("utf-8")
    ).hexdigest()

    return Expression(
        id=identifier,
        meaning_id=meaning_id,
        expression_id=expression_id,
        created_at=created_at,
    )
