"""Minimal immutable Σ essence/ground primitive for theNet."""

from __future__ import annotations

from collections.abc import Iterable
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
        {"relation_ids": relation_ids, "version": 1},
        sort_keys=True,
        separators=(",", ":"),
    )


def create_essence(relation_ids: Iterable[str]) -> Essence:
    items = tuple(relation_ids)

    if any(not isinstance(value, str) or not value.strip() for value in items):
        raise ValueError("relation_ids must contain only non-empty strings")

    canonical_ids = tuple(sorted(set(items)))
    identifier = sha256(_canonical(canonical_ids).encode("utf-8")).hexdigest()

    return Essence(id=identifier, relation_ids=canonical_ids)


__all__ = ["Essence", "create_essence"]
