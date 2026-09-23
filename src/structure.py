"""Minimal immutable Φ relational structure primitive for theNet."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
import json

from src.relation import Relation


@dataclass(frozen=True)
class PhiStructure:
    id: str
    relation_ids: tuple[str, ...]
    node_ids: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    version: int = 1

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def node_count(self) -> int:
        return len(self.node_ids)


Structure = PhiStructure


def _canonical(
    relation_ids: tuple[str, ...],
    node_ids: tuple[str, ...],
    edges: tuple[tuple[str, str], ...],
) -> str:
    return json.dumps(
        {
            "edges": edges,
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

    unique = {relation.id: relation for relation in items}
    ordered = tuple(unique[key] for key in sorted(unique))
    relation_ids = tuple(relation.id for relation in ordered)
    node_ids = tuple(
        sorted(
            {
                node_id
                for relation in ordered
                for node_id in (relation.source_id, relation.target_id)
            }
        )
    )
    edges = tuple((relation.source_id, relation.target_id) for relation in ordered)

    identifier = sha256(
        _canonical(relation_ids, node_ids, edges).encode("utf-8")
    ).hexdigest()

    return PhiStructure(
        id=identifier,
        relation_ids=relation_ids,
        node_ids=node_ids,
        edges=edges,
    )


def create_structure(relations: Iterable[Relation]) -> PhiStructure:
    return create_phi_structure(relations)
