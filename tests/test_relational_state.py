from dataclasses import FrozenInstanceError

import pytest

from src.relation import create_relation
from src.relational_state import create_relational_state


def relation(source: str, target: str, kind: str, created_at: str):
    return create_relation(source, target, kind, created_at)


def test_creates_empty_relational_state():
    state = create_relational_state("a", [])

    assert state.subject_id == "a"
    assert state.relation_ids == ()
    assert state.relation_count == 0


def test_state_contains_subject_relations():
    rel = relation("a", "b", "knows", "2026-01-01")

    state = create_relational_state("a", [rel])

    assert state.relation_ids == (rel.id,)
    assert state.relation_count == 1


def test_input_order_does_not_change_identity():
    first = relation("a", "b", "knows", "2026-01-01")
    second = relation("c", "a", "supports", "2026-01-02")

    left = create_relational_state("a", [first, second])
    right = create_relational_state("a", [second, first])

    assert left.id == right.id
    assert left.relation_ids == right.relation_ids


def test_duplicate_relations_are_deduplicated():
    rel = relation("a", "b", "knows", "2026-01-01")

    state = create_relational_state("a", [rel, rel])

    assert state.relation_ids == (rel.id,)
    assert state.relation_count == 1


def test_unrelated_relation_is_rejected():
    rel = relation("b", "c", "knows", "2026-01-01")

    with pytest.raises(ValueError):
        create_relational_state("a", [rel])


def test_invalid_subject_is_rejected():
    with pytest.raises(ValueError):
        create_relational_state(" ", [])


def test_non_relation_is_rejected():
    with pytest.raises(TypeError):
        create_relational_state("a", ["not-a-relation"])


def test_relation_change_changes_state_identity():
    first = relation("a", "b", "knows", "2026-01-01")
    second = relation("a", "c", "knows", "2026-01-01")

    left = create_relational_state("a", [first])
    right = create_relational_state("a", [second])

    assert left.id != right.id


def test_state_is_immutable():
    state = create_relational_state("a", [])

    with pytest.raises(FrozenInstanceError):
        state.relation_count = 1
