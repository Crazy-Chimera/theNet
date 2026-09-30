"""Canonical Φ structural entry point for theNet."""

from __future__ import annotations

from collections.abc import Iterable

from src.relation import Relation
from src.state import Observation
from src.structure import PhiStructure, create_phi_structure as _create_phi_structure


def create_phi_structure(relations: Iterable[Relation]) -> PhiStructure:
    """Build the canonical immutable Φ topology from Relation objects."""
    return _create_phi_structure(relations)


def create_phi_from_observation(
    observation: Observation,
    relations: Iterable[Relation],
) -> PhiStructure:
    """Materialize Φ from an observation and its referenced local relations."""
    if not isinstance(observation, Observation):
        raise TypeError("observation must be an Observation")

    items = tuple(relations)
    if any(not isinstance(relation, Relation) for relation in items):
        raise TypeError("relations must contain only Relation objects")

    expected = tuple(sorted(observation.relation_ids))
    actual = tuple(sorted({relation.id for relation in items}))

    if expected != actual:
        raise ValueError(
            "relations must exactly match observation.relation_ids"
        )

    return _create_phi_structure(items)


def create_phi(relations: Iterable[Relation]) -> PhiStructure:
    """Compatibility alias for the canonical Φ constructor."""
    return _create_phi_structure(relations)


__all__ = [
    "PhiStructure",
    "create_phi",
    "create_phi_from_observation",
    "create_phi_structure",
]
