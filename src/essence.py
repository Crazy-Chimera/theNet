"""Minimal immutable Σ essence/ground primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class Essence:
    id: str
    relation_ids: tuple[str, ...]
    version: int = 1


def _canonical(relation_ids: tuple[str, ...]) -> str:
    return json.dumps(
        {
            "relation_ids": relation_ids,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_essence(relation_ids: tuple[str, ...] | list[str] | set[str]) -> Essence:
    normalized = []
    for relation_id in relation_ids:
        if not isinstance(relation_id, str) or not relation_id.strip():
            raise ValueError("relation_ids must contain only non-empty strings")
        normalized.append(relation_id)

    canonical_ids = tuple(sorted(set(normalized)))
    identifier = sha256(_canonical(canonical_ids).encode("utf-8")).hexdigest()

    return Essence(id=identifier, relation_ids=canonical_ids)
