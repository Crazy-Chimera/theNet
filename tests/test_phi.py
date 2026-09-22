from dataclasses import FrozenInstanceError

import pytest

from src.genesis import create_genesis
from src.relation import create_relation
from src.phi import PhiStructure, create_phi, create_phi_structure


STAMP = "2026-09-22T00:00:00Z"


def make_relation(source: str, target: str, kind: str = "connect"):
    return create_relation(source, target, kind, STAMP)


def test_phi_entry_point_uses_canonical_structure():
    relation = make_relation("a", "b")
    state = create_phi_structure([relation])

    assert isinstance(state, PhiStructure)
    assert state.relation_ids == (relation.id,)
    assert state.edges == (("a", "b"),)


def test_phi_is_order_independent_and_deduplicates():
    first = make_relation("a", "b")
    second = make_relation("b", "c")

    assert create_phi_structure([first, second, first]) == create_phi_structure([second, first])


def test_empty_phi_is_valid():
    state = create_phi_structure([])

    assert state.relation_ids == ()
    assert state.node_ids == ()
    assert state.edges == ()


def test_structural_change_changes_identity():
    first = make_relation("a", "b")
    second = make_relation("b", "c")

    assert create_phi_structure([first]).id != create_phi_structure([first, second]).id


def test_invalid_relation_is_rejected():
    with pytest.raises(TypeError):
        create_phi_structure([object()])


def test_phi_is_immutable():
    state = create_phi_structure([make_relation("a", "b")])

    with pytest.raises(FrozenInstanceError):
        state.version = 2


def test_phi_compatibility_alias():
    relation = make_relation("a", "b")
    assert create_phi([relation]) == create_phi_structure([relation])


def test_genesis_identifiers_can_form_phi_edges():
    a = create_genesis("a", STAMP)
    b = create_genesis("b", STAMP)
    relation = create_relation(a.id, b.id, "knows", STAMP)
    state = create_phi([relation])

    assert state.node_ids == tuple(sorted((a.id, b.id)))
    assert state.edges == ((a.id, b.id),)
