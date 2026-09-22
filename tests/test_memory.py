from dataclasses import FrozenInstanceError

import pytest

from src.memory import create_memory


def test_memory_creation():
    memory = create_memory("agent-a", "state-1", "observation", "2026-09-22T08:00:00Z")

    assert len(memory.id) == 64
    assert memory.subject_id == "agent-a"
    assert memory.source_id == "state-1"
    assert memory.kind == "observation"
    assert memory.version == 1


def test_memory_is_deterministic():
    args = ("agent-a", "state-1", "observation", "t")
    assert create_memory(*args) == create_memory(*args)


@pytest.mark.parametrize("index", range(4))
def test_each_memory_field_changes_identity(index):
    base = ["agent-a", "state-1", "observation", "t"]
    changed = base.copy()
    changed[index] += "-changed"

    assert create_memory(*base).id != create_memory(*changed).id


@pytest.mark.parametrize(
    "kwargs",
    [
        {"subject_id": "", "source_id": "s", "kind": "k", "created_at": "t"},
        {"subject_id": "a", "source_id": "", "kind": "k", "created_at": "t"},
        {"subject_id": "a", "source_id": "s", "kind": "", "created_at": "t"},
        {"subject_id": "a", "source_id": "s", "kind": "k", "created_at": ""},
    ],
)
def test_empty_fields_are_rejected(kwargs):
    with pytest.raises(ValueError):
        create_memory(**kwargs)


def test_memory_is_immutable():
    memory = create_memory("a", "s", "k", "t")

    with pytest.raises(FrozenInstanceError):
        memory.kind = "changed"
