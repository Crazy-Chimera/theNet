from dataclasses import FrozenInstanceError

import pytest

from src.phi import create_phi, create_phi_structure


def test_phi_structure_creation():
    state = create_phi_structure(["b", "a"], ["r2", "r1"])
    assert state.node_ids == ("a", "b")
    assert state.relation_ids == ("r1", "r2")
    assert state.density == 1.0
    assert state.version == 1
    assert len(state.id) == 64


def test_phi_identity_is_deterministic():
    first = create_phi_structure(["b", "a"], ["r2", "r1"])
    second = create_phi_structure(["a", "b"], ["r1", "r2"])
    assert first == second


def test_phi_density_for_partial_structure():
    state = create_phi_structure(["a", "b", "c"], ["r1"])
    assert state.density == pytest.approx(1 / 6)


def test_single_node_has_zero_density():
    state = create_phi_structure(["a"], [])
    assert state.density == 0.0


def test_empty_nodes_are_rejected():
    with pytest.raises(ValueError, match="node_ids"):
        create_phi_structure([], [])


@pytest.mark.parametrize(
    "nodes, relations, field",
    [
        (["a", "a"], [], "node_ids"),
        (["a", ""], [], "node_ids"),
        (["a"], ["r1", "r1"], "relation_ids"),
        (["a"], ["r1", ""], "relation_ids"),
    ],
)
def test_invalid_identifiers_are_rejected(nodes, relations, field):
    with pytest.raises(ValueError, match=field):
        create_phi_structure(nodes, relations)


def test_phi_is_immutable():
    state = create_phi_structure(["a", "b"], ["r1"])
    with pytest.raises(FrozenInstanceError):
        state.density = 0.5


def test_structural_change_changes_identity():
    first = create_phi_structure(["a", "b"], ["r1"])
    second = create_phi_structure(["a", "b"], ["r2"])
    assert first.id != second.id


def test_create_phi_adapts_relations():
    class Relation:
        id = "r1"
        source_id = "a"
        target_id = "b"

    state = create_phi([Relation()])

    assert state.relation_ids == ("r1",)
    assert state.node_ids == ("a", "b")
