from dataclasses import FrozenInstanceError

import pytest

from src.relation import create_relation
from src.structure import PhiStructure, create_phi_structure


def make_relation(source: str, target: str, kind: str = "connect"):
    return create_relation(source, target, kind, "2026-09-21T00:00:00Z")


def test_phi_collects_unique_sorted_nodes_and_relations():
    first = make_relation("b", "c")
    second = make_relation("a", "b")

    result = create_phi_structure([first, second, first])

    assert isinstance(result, PhiStructure)
    assert result.node_ids == ("a", "b", "c")
    assert result.relation_ids == tuple(sorted((first.id, second.id)))
    assert result.edges == (("a", "b"), ("b", "c"))
    assert result.version == 1


def test_phi_identity_is_independent_of_relation_order():
    first = make_relation("a", "b")
    second = make_relation("b", "c")

    left = create_phi_structure([first, second])
    right = create_phi_structure([second, first])

    assert left.id == right.id


def test_empty_relation_collection_is_valid():
    result = create_phi_structure([])

    assert result.relation_ids == ()
    assert result.node_ids == ()
    assert len(result.id) == 64


def test_adding_relation_changes_phi_identity():
    first = make_relation("a", "b")
    second = make_relation("b", "c")

    assert create_phi_structure([first]).id != create_phi_structure([first, second]).id


def test_changed_relation_id_changes_phi_identity():
    first = make_relation("a", "b")
    changed = make_relation("a", "b", "different")

    assert first.id != changed.id
    assert create_phi_structure([first]).id != create_phi_structure([changed]).id


def test_phi_is_immutable():
    result = create_phi_structure([make_relation("a", "b")])

    with pytest.raises(FrozenInstanceError):
        result.version = 2


def test_invalid_relation_is_rejected():
    with pytest.raises(TypeError):
        create_phi_structure([object()])


def test_input_relations_are_not_mutated():
    first = make_relation("a", "b")
    before = first

    create_phi_structure([first])

    assert first == before


def test_generator_input_is_supported():
    first = make_relation("a", "b")
    second = make_relation("b", "c")

    result = create_phi_structure(item for item in [first, second])

    assert result.node_ids == ("a", "b", "c")
