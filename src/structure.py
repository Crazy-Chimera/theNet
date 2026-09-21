"""Minimal immutable Φ relational structure primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from collections.abc import Iterable
import json

from src.relation import Relation


@dataclass(frozen=True)
class PhiStructure:
    id: str
    relation_ids: tuple[str, ...]
    node_ids: tuple[str, ...]
    version: int = 1


def _canonical(
    relation_ids: tuple[str, ...],
    node_ids: tuple[str, ...],
) -> str:
    return json.dumps(
        {
            "node_ids": node_ids,
            "relation_ids": relation_ids,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_phi_structure(relations: Iterable[Relation]) -> PhiStructure:
    items = tuple(relations)

    if any(not isinstance(relation, Relation) for relation in items):
        raise TypeError("relations must contain only Relation objects")

    relation_ids = tuple(sorted({relation.id for relation in items}))
    node_ids = tuple(
        sorted(
            {
                node_id
                for relation in items
                for node_id in (relation.source_id, relation.target_id)
            }
        )
    )

    identifier = sha256(
        _canonical(relation_ids, node_ids).encode("utf-8")
    ).hexdigest()

    return PhiStructure(
        id=identifier,
        relation_ids=relation_ids,
        node_ids=node_ids,
    )
