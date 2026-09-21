"""Minimal immutable structural fingerprint for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class PhiStructure:
    id: str
    subject_id: str
    relation_ids: tuple[str, ...]
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


def create_phi_structure(
    subject_id: str,
    relation_ids: list[str] | tuple[str, ...],
) -> PhiStructure:
    if not isinstance(subject_id, str) or not subject_id.strip():
        raise ValueError("subject_id must be non-empty")
    if not isinstance(relation_ids, (list, tuple)):
        raise ValueError("relation_ids must be a list or tuple")

    normalized: set[str] = set()
    for relation_id in relation_ids:
        if not isinstance(relation_id, str) or not relation_id.strip():
            raise ValueError("relation_ids must contain only non-empty strings")
        normalized.add(relation_id)

    canonical_relations = tuple(sorted(normalized))
    identifier = sha256(
        _canonical(subject_id, canonical_relations).encode("utf-8")
    ).hexdigest()

    return PhiStructure(
        id=identifier,
        subject_id=subject_id,
        relation_ids=canonical_relations,
    )
