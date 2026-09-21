from dataclasses import FrozenInstanceError

import pytest

from src.relation import create_relation


STAMP = "2026-09-21T00:00:00Z"


def test_create_relation():
    relation = create_relation("agent:a", "agent:b", "trust", STAMP)

    assert relation.source_id == "agent:a"
    assert relation.target_id == "agent:b"
    assert relation.kind == "trust"
    assert relation.created_at == STAMP
    assert relation.version == 1
    assert len(relation.id) == 64


def test_relation_is_deterministic():
    first = create_relation("agent:a", "agent:b", "trust", STAMP)
    second = create_relation("agent:a", "agent:b", "trust", STAMP)

    assert first == second


@pytest.mark.parametrize(
    ("source_id", "target_id", "kind", "created_at"),
    [
        ("", "agent:b", "trust", STAMP),
        ("agent:a", "", "trust", STAMP),
        ("agent:a", "agent:b", "", STAMP),
        ("agent:a", "agent:b", "trust", ""),
    ],
)
def test_empty_fields_are_rejected(source_id, target_id, kind, created_at):
    with pytest.raises(ValueError):
        create_relation(source_id, target_id, kind, created_at)


def test_relation_is_immutable():
    relation = create_relation("agent:a", "agent:b", "trust", STAMP)

    with pytest.raises(FrozenInstanceError):
        relation.kind = "other"


def test_relation_is_directed():
    forward = create_relation("agent:a", "agent:b", "trust", STAMP)
    reverse = create_relation("agent:b", "agent:a", "trust", STAMP)

    assert forward.id != reverse.id
    assert forward.source_id != forward.target_id


def test_relation_kind_changes_identity():
    trust = create_relation("agent:a", "agent:b", "trust", STAMP)
    observation = create_relation("agent:a", "agent:b", "observation", STAMP)

    assert trust.id != observation.id
