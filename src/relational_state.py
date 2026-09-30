"""Deterministic immutable Relational State for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from src.relation import Relation


@dataclass(frozen=True)
class RelationalState:
    id: str
    subject_id: str
    relation_ids: tuple[str, ...]
    relation_count: int
    version: int = 1


def _canonical(subject_id: str, relation_ids: tuple[str, ...]) -> str:
    return json.dumps(
        {
            "relation_ids": relation_ids,
            "subject_id": subject_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_relational_state(
    subject_id: str,
    relations: tuple[Relation, ...] | list[Relation],
) -> RelationalState:
    if not isinstance(subject_id, str) or not subject_id.strip():
        raise ValueError("subject_id must be non-empty")

    relation_ids: set[str] = set()

    for relation in relations:
        if not isinstance(relation, Relation):
            raise TypeError("relations must contain Relation objects")
        if subject_id not in (relation.source_id, relation.target_id):
            raise ValueError("relation does not belong to subject_id")
        relation_ids.add(relation.id)

    canonical_ids = tuple(sorted(relation_ids))
    identifier = sha256(
        _canonical(subject_id, canonical_ids).encode("utf-8")
    ).hexdigest()

    return RelationalState(
        id=identifier,
        subject_id=subject_id,
        relation_ids=canonical_ids,
        relation_count=len(canonical_ids),
    )
