from dataclasses import FrozenInstanceError

import pytest

from src.sigma import Essence, create_essence


def test_empty_ground_is_valid():
    state = create_essence([])
    assert isinstance(state, Essence)
    assert state.relation_ids == ()


def test_essence_is_order_independent_and_deduplicates():
    assert create_essence(["b", "a", "b"]) == create_essence(["a", "b"])


def test_invalid_relation_identifier_is_rejected():
    with pytest.raises(ValueError):
        create_essence(["ok", ""])


def test_essence_identity_changes_with_relation_context():
    assert create_essence(["a"]).id != create_essence(["a", "b"]).id


def test_essence_is_immutable():
    state = create_essence(["a"])
    with pytest.raises(FrozenInstanceError):
        state.version = 2
