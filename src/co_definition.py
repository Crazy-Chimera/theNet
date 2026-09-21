"""Minimal immutable Ρ relational co-definition primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class RelationalCoDefinition:
    id: str
    left_id: str
    right_id: str
    relation_kind: str
    created_at: str
    version: int = 1


def _canonical(
    left_id: str,
    right_id: str,
    relation_kind: str,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "created_at": created_at,
            "left_id": left_id,
            "relation_kind": relation_kind,
            "right_id": right_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_co_definition(
    left_id: str,
    right_id: str,
    relation_kind: str,
    created_at: str,
) -> RelationalCoDefinition:
    for name, value in {
        "left_id": left_id,
        "right_id": right_id,
        "relation_kind": relation_kind,
        "created_at": created_at,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    identifier = sha256(
        _canonical(
            left_id,
            right_id,
            relation_kind,
            created_at,
        ).encode("utf-8")
    ).hexdigest()

    return RelationalCoDefinition(
        id=identifier,
        left_id=left_id,
        right_id=right_id,
        relation_kind=relation_kind,
        created_at=created_at,
    )
