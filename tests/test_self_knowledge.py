from dataclasses import FrozenInstanceError

import pytest

from src.self_knowledge import SelfKnowledge, create_self_knowledge


def make_self_knowledge():
    return create_self_knowledge(
        "subject-a",
        "structure-a",
        "memory-a",
        "2026-09-21T00:00:00Z",
    )


def test_create_self_knowledge():
    result = make_self_knowledge()

    assert isinstance(result, SelfKnowledge)
    assert result.subject_id == "subject-a"
    assert result.structure_id == "structure-a"
    assert result.memory_id == "memory-a"
    assert result.version == 1
    assert len(result.id) == 64


def test_identity_is_deterministic():
    assert make_self_knowledge().id == make_self_knowledge().id


@pytest.mark.parametrize(
    "field,value",
    [
        ("subject_id", ""),
        ("structure_id", ""),
        ("memory_id", ""),
        ("created_at", ""),
    ],
)
def test_empty_fields_are_rejected(field, value):
    values = {
        "subject_id": "subject-a",
        "structure_id": "structure-a",
        "memory_id": "memory-a",
        "created_at": "2026-09-21T00:00:00Z",
    }
    values[field] = value

    with pytest.raises(ValueError):
        create_self_knowledge(**values)


@pytest.mark.parametrize(
    "field,value",
    [
        ("subject_id", "subject-b"),
        ("structure_id", "structure-b"),
        ("memory_id", "memory-b"),
        ("created_at", "2026-09-22T00:00:00Z"),
    ],
)
def test_changing_any_defining_input_changes_identity(field, value):
    values = {
        "subject_id": "subject-a",
        "structure_id": "structure-a",
        "memory_id": "memory-a",
        "created_at": "2026-09-21T00:00:00Z",
    }
    values[field] = value

    assert create_self_knowledge(**values).id != make_self_knowledge().id


def test_self_knowledge_is_immutable():
    result = make_self_knowledge()

    with pytest.raises(FrozenInstanceError):
        result.memory_id = "other-memory"


def test_inputs_are_not_mutated():
    values = {
        "subject_id": "subject-a",
        "structure_id": "structure-a",
        "memory_id": "memory-a",
        "created_at": "2026-09-21T00:00:00Z",
    }
    before = values.copy()

    create_self_knowledge(**values)

    assert values == before
