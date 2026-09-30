import os

import pytest

from src.genesis import create_genesis
from src.relation import create_relation
from src.sqlite_store import SQLiteStore
from src.postgres_store import PostgresStore


STAMP = "2026-09-30T00:00:00Z"


@pytest.fixture(params=["sqlite", "postgres"])
def store(request):
    if request.param == "sqlite":
        instance = SQLiteStore()
    else:
        dsn = os.getenv("THENET_POSTGRES_DSN")
        if not dsn:
            pytest.skip("THENET_POSTGRES_DSN is not configured")
        instance = PostgresStore(dsn)

    try:
        yield instance
    finally:
        instance.close()


def test_backend_exposes_runtime_store_operations(store):
    for method in (
        "save_genesis",
        "get_genesis",
        "save_relation",
        "get_relation",
        "close",
    ):
        assert callable(getattr(store, method))


def test_genesis_round_trip_is_backend_independent(store):
    state = create_genesis("agent:contract", STAMP)

    store.save_genesis(state)
    loaded = store.get_genesis(state.id)

    assert loaded == state
    assert loaded is not state


def test_relation_round_trip_is_backend_independent(store):
    relation = create_relation("agent:a", "agent:b", "trust", STAMP)

    store.save_relation(relation)
    loaded = store.get_relation(relation.id)

    assert loaded == relation
    assert loaded is not relation


def test_unknown_ids_are_backend_independent(store):
    assert store.get_genesis("missing-genesis") is None
    assert store.get_relation("missing-relation") is None


def test_repeated_saves_are_backend_independent(store):
    state = create_genesis("agent:idempotent", STAMP)
    relation = create_relation("agent:a", "agent:b", "trust", STAMP)

    store.save_genesis(state)
    store.save_genesis(state)
    store.save_relation(relation)
    store.save_relation(relation)

    assert store.get_genesis(state.id) == state
    assert store.get_relation(relation.id) == relation


def test_conflicting_identifiers_are_backend_independent(store):
    first = create_genesis("agent:first", STAMP)
    conflicting = type(first)(
        id=first.id,
        subject="agent:conflict",
        created_at=first.created_at,
        relations=(),
        version=first.version,
    )

    store.save_genesis(first)

    with pytest.raises(ValueError, match="storage conflict"):
        store.save_genesis(conflicting)

    assert store.get_genesis(first.id) == first
