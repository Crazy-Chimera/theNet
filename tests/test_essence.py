from dataclasses import FrozenInstanceError

import pytest

from src.essence import create_essence


def test_create_essence():
    item = create_essence(["rel-b", "rel-a"])

    assert item.relation_ids == ("rel-a", "rel-b")
    assert item.version == 1
    assert len(item.id) == 64


def test_empty_context_is_valid():
    item = create_essence([])

    assert item.relation_ids == ()
    assert len(item.id) == 64


def test_identity_is_order_independent():
    assert create_essence(["rel-a", "rel-b"]).id == create_essence(
        ["rel-b", "rel-a"]
    ).id


def test_duplicates_are_collapsed():
    assert create_essence(["rel-a", "rel-a"]).relation_ids == ("rel-a",)


@pytest.mark.parametrize("value", [["rel-a", ""], ["rel-a", "   "], ["rel-a", None]])
def test_invalid_relation_identifier_is_rejected(value):
    with pytest.raises(ValueError):
        create_essence(value)


def test_result_is_immutable():
    item = create_essence(["rel-a"])

    with pytest.raises(FrozenInstanceError):
        item.relation_ids = ("rel-b",)


def test_defining_relation_changes_change_identity():
    base = create_essence(["rel-a"])

    assert create_essence(["rel-b"]).id != base.id
