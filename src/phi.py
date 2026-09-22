"""Minimal immutable structural Φ snapshot for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable


@dataclass(frozen=True)
class PhiStructure:
    id: str
    node_ids: tuple[str, ...]
    relation_ids: tuple[str, ...]
    density: float
    version: int = 1


def _validate_ids(values: tuple[str, ...], name: str) -> None:
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"{name} must contain only non-empty strings")
    if len(values) != len(set(values)):
        raise ValueError(f"{name} must not contain duplicates")


def _canonical(node_ids: tuple[str, ...], relation_ids: tuple[str, ...]) -> str:
    return json.dumps(
        {"node_ids": node_ids, "relation_ids": relation_ids, "version": 1},
        sort_keys=True,
        separators=(",", ":"),
    )


def create_phi_structure(
    node_ids: tuple[str, ...] | list[str],
    relation_ids: tuple[str, ...] | list[str],
) -> PhiStructure:
    nodes = tuple(sorted(node_ids))
    relations = tuple(sorted(relation_ids))

    if not nodes:
        raise ValueError("node_ids must be non-empty")

    _validate_ids(nodes, "node_ids")
    _validate_ids(relations, "relation_ids")

    node_count = len(nodes)
    possible_relations = node_count * (node_count - 1)
    density = (
        min(1.0, len(relations) / possible_relations)
        if possible_relations
        else 0.0
    )

    identifier = sha256(
        _canonical(nodes, relations).encode("utf-8")
    ).hexdigest()

    return PhiStructure(
        id=identifier,
        node_ids=nodes,
        relation_ids=relations,
        density=density,
    )


def create_phi(relations: Iterable[object]) -> PhiStructure:
    """Build Φ directly from theNet Relation objects.

    This adapter keeps the structural primitive independent of the Relation
    implementation while providing the integration API used by the closure.
    """
    relation_list = tuple(relations)
    relation_ids: list[str] = []
    node_ids: set[str] = set()

    for relation in relation_list:
        relation_id = getattr(relation, "id", None)
        source_id = getattr(relation, "source_id", None)
        target_id = getattr(relation, "target_id", None)

        if not all(
            isinstance(value, str) and value.strip()
            for value in (relation_id, source_id, target_id)
        ):
            raise ValueError("relations must expose valid id, source_id, and target_id")

        relation_ids.append(relation_id)
        node_ids.update((source_id, target_id))

    if not relation_list:
        raise ValueError("relations must be non-empty")

    return create_phi_structure(tuple(node_ids), relation_ids)
