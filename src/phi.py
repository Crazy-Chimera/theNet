"""Minimal immutable Φ structural representation for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable


@dataclass(frozen=True)
class PhiStructure:
    id: str
    relation_ids: tuple[str, ...]
    node_ids: tuple[str, ...]
    version: int = 1


def _canonical(relation_ids: tuple[str, ...], node_ids: tuple[str, ...]) -> str:
    return json.dumps(
        {
            "node_ids": node_ids,
            "relation_ids": relation_ids,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_phi(relations: Iterable[object]) -> PhiStructure:
    relation_ids: set[str] = set()
    node_ids: set[str] = set()

    for relation in relations:
        relation_id = getattr(relation, "id", None)
        source_id = getattr(relation, "source_id", None)
        target_id = getattr(relation, "target_id", None)

        for name, value in (
            ("relation.id", relation_id),
            ("relation.source_id", source_id),
            ("relation.target_id", target_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")

        relation_ids.add(relation_id)
        node_ids.update((source_id, target_id))

    ordered_relations = tuple(sorted(relation_ids))
    ordered_nodes = tuple(sorted(node_ids))
    identifier = sha256(
        _canonical(ordered_relations, ordered_nodes).encode("utf-8")
    ).hexdigest()

    return PhiStructure(
        id=identifier,
        relation_ids=ordered_relations,
        node_ids=ordered_nodes,
    )
