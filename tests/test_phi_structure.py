from dataclasses import FrozenInstanceError

import pytest

from src.genesis import create_genesis
from src.relation import create_relation
from src.phi_structure import PhiStructure, create_phi_structure


def make_relation(source: str, target: str, kind: str = "connect"):
    return create_relation(source, target, kind, "2026-09-22T00:00:00Z")


def test_phi_structure_builds_canonical_topology():
    a = create_genesis("a", "2026-09-22T00:00:00Z")
    b = create_genesis("b", "2026-09-22T00:00:00Z")
    relation = create_relation(a.id, b.id, "knows", "2026-09-22T00:01:00Z")
    result = create_phi_structure([relation])
    assert isinstance(result, PhiStructure)
    assert result.relation_ids == (relation.id,)
    assert result.node_ids == tuple(sorted((a.id, b.id)))
    assert result.edges == ((a.id, b.id),)


def test_phi_structure_is_order_independent_and_deduplicates():
    first = make_relation("a", "b")
    second = make_relation("b", "c")
    assert create_phi_structure([first, second, first]) == create_phi_structure([second, first])


def test_empty_phi_structure_is_valid():
    result = create_phi_structure([])
    assert result.relation_ids == ()
    assert result.node_ids == ()
    assert result.edges == ()
    assert len(result.id) == 64


def test_relation_membership_changes_identity():
    first = make_relation("a", "b")
    second = make_relation("b", "c")
    assert create_phi_structure([first]).id != create_phi_structure([first, second]).id


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
    assert result.edges == (("a", "b"), ("b", "c"))
