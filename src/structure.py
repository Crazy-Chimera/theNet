"""Minimal immutable Φ structural fingerprint for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable


@dataclass(frozen=True)
class Structure:
    id: str
    relation_ids: tuple[str, ...]
    node_ids: tuple[str, ...]
    edge_count: int
    node_count: int
    version: int = 1


def _canonical(relation_ids: tuple[str, ...]) -> str:
    return json.dumps(
        {"relation_ids": relation_ids, "version": 1},
        sort_keys=True,
        separators=(",", ":"),
    )


def create_structure(relations: Iterable[object]) -> Structure:
    relation_list = tuple(relations)
    relation_ids = tuple(
        sorted(_relation_id(relation) for relation in relation_list)
    )

    if len(set(relation_ids)) != len(relation_ids):
        raise ValueError("relation IDs must be unique")

    nodes = {
        node_id
        for relation in relation_list
        for node_id in (_endpoint(relation, "source_id"), _endpoint(relation, "target_id"))
    }
    node_ids = tuple(sorted(nodes))

    identifier = sha256(
        _canonical(relation_ids).encode("utf-8")
    ).hexdigest()

    return Structure(
        id=identifier,
        relation_ids=relation_ids,
        node_ids=node_ids,
        edge_count=len(relation_ids),
        node_count=len(node_ids),
    )


def _relation_id(relation: object) -> str:
    value = getattr(relation, "id", None)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("relation id must be non-empty")
    return value


def _endpoint(relation: object, name: str) -> str:
    value = getattr(relation, name, None)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty")
    return value
