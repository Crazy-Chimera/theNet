"""Minimal immutable directed Relation primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class Relation:
    id: str
    source_id: str
    target_id: str
    kind: str
    created_at: str
    version: int = 1


def _canonical(
    source_id: str,
    target_id: str,
    kind: str,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "created_at": created_at,
            "kind": kind,
            "source_id": source_id,
            "target_id": target_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_relation(
    source_id: str,
    target_id: str,
    kind: str,
    created_at: str,
) -> Relation:
    values = {
        "source_id": source_id,
        "target_id": target_id,
        "kind": kind,
        "created_at": created_at,
    }
    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    identifier = sha256(
        _canonical(source_id, target_id, kind, created_at).encode("utf-8")
    ).hexdigest()

    return Relation(
        id=identifier,
        source_id=source_id,
        target_id=target_id,
        kind=kind,
        created_at=created_at,
    )
