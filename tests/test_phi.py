from dataclasses import FrozenInstanceError

import pytest

from src.genesis import create_genesis
from src.relation import create_relation
from src.phi import create_phi


def test_phi_captures_relations_and_nodes():
    a = create_genesis("a", "2026-09-21T00:00:00Z")
    b = create_genesis("b", "2026-09-21T00:00:00Z")
    relation = create_relation(a.id, b.id, "knows", "2026-09-21T00:01:00Z")

    phi = create_phi([relation])

    assert phi.relation_ids == (relation.id,)
    assert phi.node_ids == tuple(sorted((a.id, b.id)))
    assert len(phi.id) == 64


def test_phi_is_order_independent_and_deduplicates_relations():
    a = create_genesis("a", "2026-09-21T00:00:00Z")
    b = create_genesis("b", "2026-09-21T00:00:00Z")
    c = create_genesis("c", "2026-09-21T00:00:00Z")
    ab = create_relation(a.id, b.id, "knows", "2026-09-21T00:01:00Z")
    bc = create_relation(b.id, c.id, "knows", "2026-09-21T00:02:00Z")

    left = create_phi([ab, bc, ab])
    right = create_phi([bc, ab])

    assert left == right


def test_empty_phi_is_valid():
    phi = create_phi([])

    assert phi.relation_ids == ()
    assert phi.node_ids == ()
    assert len(phi.id) == 64


def test_phi_rejects_invalid_relation_fields():
    class Invalid:
        id = "relation"
        source_id = ""
        target_id = "target"

    with pytest.raises(TypeError):
        create_phi([Invalid()])


def test_phi_is_immutable():
    phi = create_phi([])

    with pytest.raises(FrozenInstanceError):
        phi.version = 2


def test_phi_does_not_mutate_input_collection():
    a = create_genesis("a", "2026-09-21T00:00:00Z")
    b = create_genesis("b", "2026-09-21T00:00:00Z")
    relation = create_relation(a.id, b.id, "knows", "2026-09-21T00:01:00Z")
    relations = [relation]

    create_phi(relations)

    assert relations == [relation]


def test_public_phi_api_uses_canonical_topology():
    from src.phi_coherence import phi_coherence
    from src.structure import PhiStructure

    a = create_genesis("a", "2026-09-22T00:00:00Z")
    b = create_genesis("b", "2026-09-22T00:00:00Z")
    relation = create_relation(a.id, b.id, "knows", "2026-09-22T00:01:00Z")

    phi = create_phi([relation])

    assert isinstance(phi, PhiStructure)
    assert phi.edges == ((a.id, b.id),)
    assert phi_coherence(phi) == 1.0
