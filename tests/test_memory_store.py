from dataclasses import FrozenInstanceError

import pytest

from src.memory_store import (
    SQLiteMemoryStore,
    create_episodic_memory,
    create_procedural_skill,
    create_semantic_memory,
)


STAMP = "2026-09-30T00:00:00Z"


def test_store_has_three_memory_tables():
    with SQLiteMemoryStore() as store:
        assert store.table_names() == (
            "episodic_memory",
            "procedural_memory",
            "semantic_memory",
        )


def test_episodic_round_trip_and_reopen(tmp_path):
    path = tmp_path / "memory.sqlite"
    memory = create_episodic_memory("agent:a", "source:1", "observed relation", STAMP)

    with SQLiteMemoryStore(path) as store:
        store.save_episodic(memory)

    with SQLiteMemoryStore(path) as reopened:
        assert reopened.get_episodic(memory.id) == memory
        assert reopened.list_episodic() == (memory,)


def test_semantic_round_trip_and_confidence_bounds():
    memory = create_semantic_memory("agent:a", "pattern:a", 0.8, STAMP)

    with SQLiteMemoryStore() as store:
        store.save_semantic(memory)
        assert store.get_semantic(memory.id) == memory

    with pytest.raises(ValueError):
        create_semantic_memory("agent:a", "pattern:a", 1.1, STAMP)


def test_procedural_skill_updates_are_consistent():
    skill = create_procedural_skill("agent:a", "proposal-review", STAMP)

    with SQLiteMemoryStore() as store:
        store.save_procedural(skill)
        first = store.update_procedural(skill.id, success=True)
        second = store.update_procedural(skill.id, success=False)

        assert first.success_count == 1
        assert first.failure_count == 0
        assert second.success_count == 1
        assert second.failure_count == 1
        assert second.version == 3


def test_conflicting_memory_identity_is_rejected():
    first = create_episodic_memory("agent:a", "source:1", "a", STAMP)
    conflicting = type(first)(
        id=first.id,
        subject_id="agent:b",
        source_id=first.source_id,
        content="different",
        created_at=first.created_at,
    )

    with SQLiteMemoryStore() as store:
        store.save_episodic(first)
        with pytest.raises(ValueError, match="memory conflict"):
            store.save_episodic(conflicting)


def test_memory_records_are_immutable():
    memory = create_semantic_memory("agent:a", "pattern:a", 0.5, STAMP)

    with pytest.raises(FrozenInstanceError):
        memory.confidence = 1.0


@pytest.mark.parametrize(
    "factory,args",
    [
        (create_episodic_memory, ("", "source", "content", STAMP)),
        (create_episodic_memory, ("agent", "", "content", STAMP)),
        (create_semantic_memory, ("agent", "", 0.5, STAMP)),
        (create_procedural_skill, ("agent", "", STAMP)),
    ],
)
def test_invalid_memory_inputs_are_rejected(factory, args):
    with pytest.raises(ValueError):
        factory(*args)


def test_unknown_procedural_skill_is_rejected():
    with SQLiteMemoryStore() as store:
        with pytest.raises(KeyError):
            store.update_procedural("missing", success=True)
