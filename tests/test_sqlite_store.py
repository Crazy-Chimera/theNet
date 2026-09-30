import pytest

from src.genesis import create_genesis
from src.relation import create_relation
from src.sqlite_store import SQLiteStore


STAMP = "2026-09-30T00:00:00Z"


def test_genesis_round_trip():
    state = create_genesis("agent:a", STAMP)

    with SQLiteStore() as store:
        store.save_genesis(state)
        loaded = store.get_genesis(state.id)

    assert loaded == state
    assert loaded is not state


def test_relation_round_trip():
    relation = create_relation("agent:a", "agent:b", "trust", STAMP)

    with SQLiteStore() as store:
        store.save_relation(relation)
        loaded = store.get_relation(relation.id)

    assert loaded == relation
    assert loaded is not relation


def test_unknown_ids_return_none():
    with SQLiteStore() as store:
        assert store.get_genesis("missing") is None
        assert store.get_relation("missing") is None


def test_repeated_save_is_idempotent():
    state = create_genesis("agent:a", STAMP)

    with SQLiteStore() as store:
        store.save_genesis(state)
        store.save_genesis(state)

        assert store.get_genesis(state.id) == state


def test_conflicting_identifier_is_rejected():
    first = create_genesis("agent:a", STAMP)
    conflicting = type(first)(
        id=first.id,
        subject="agent:other",
        created_at=first.created_at,
        relations=(),
        version=first.version,
    )

    with SQLiteStore() as store:
        store.save_genesis(first)

        with pytest.raises(ValueError, match="storage conflict"):
            store.save_genesis(conflicting)


def test_loaded_genesis_remains_immutable():
    state = create_genesis("agent:a", STAMP)

    with SQLiteStore() as store:
        store.save_genesis(state)
        loaded = store.get_genesis(state.id)

    with pytest.raises(AttributeError):
        loaded.subject = "changed"


def test_file_backed_store_survives_reopen(tmp_path):
    path = tmp_path / "thenet.sqlite"
    relation = create_relation("agent:a", "agent:b", "trust", STAMP)

    with SQLiteStore(path) as first:
        first.save_relation(relation)

    with SQLiteStore(path) as second:
        assert second.get_relation(relation.id) == relation