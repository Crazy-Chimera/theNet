from dataclasses import FrozenInstanceError

import pytest

from src.genesis import create_genesis
from src.relation import create_relation
from src.phi_structure import PhiStructure, create_phi_structure


def make_relation(source: str, target: str, kind: str = "connect"):
    return create_relation(source, target, kind, "2026-09-22T00:00:00Z")


def test_phi_structure_contains_canonical_relation_set():
    relation = make_relation("a", "b", "knows")
    result = create_phi_structure([relation])

    assert isinstance(result, PhiStructure)
    assert result.relation_ids == (relation.id,)
    assert result.version == 1


def test_phi_structure_is_order_independent_and_deduplicates():
    first = make_relation("a", "b")
    second = make_relation("b", "c")

    assert create_phi_structure([first, second, first]) == create_phi_structure(
        [second, first]
    )


def test_empty_phi_structure_is_valid():
    result = create_phi_structure([])

    assert result.relation_ids == ()
    assert len(result.id) == 64


def test_relation_membership_changes_identity():
    first = make_relation("a", "b")
    second = make_relation("b", "c")

    assert create_phi_structure([first]).id != create_phi_structure(
        [first, second]
    ).id


def test_invalid_relation_is_rejected():
    with pytest.raises(TypeError):
        create_phi_structure([object()])


def test_phi_structure_is_immutable():
    result = create_phi_structure([make_relation("a", "b")])

    with pytest.raises(FrozenInstanceError):
        result.version = 2


def test_generator_input_is_supported():
    first = make_relation("a", "b")
    second = make_relation("b", "c")

    result = create_phi_structure(item for item in [first, second])

    assert result.relation_ids == tuple(sorted((first.id, second.id)))
