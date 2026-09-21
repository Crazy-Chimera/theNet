from dataclasses import FrozenInstanceError

import pytest

from src.co_definition import create_co_definition


def test_create_co_definition():
    item = create_co_definition("self-a", "self-b", "trust", "2026-09-21T00:00:00Z")

    assert item.left_id == "self-a"
    assert item.right_id == "self-b"
    assert item.relation_kind == "trust"
    assert item.created_at == "2026-09-21T00:00:00Z"
    assert item.version == 1
    assert len(item.id) == 64


def test_identity_is_deterministic():
    args = ("self-a", "self-b", "trust", "2026-09-21T00:00:00Z")

    assert create_co_definition(*args).id == create_co_definition(*args).id


@pytest.mark.parametrize(
    "index",
    [0, 1, 2, 3],
)
def test_empty_defining_input_is_rejected(index):
    values = ["self-a", "self-b", "trust", "2026-09-21T00:00:00Z"]
    values[index] = "   "

    with pytest.raises(ValueError):
        create_co_definition(*values)


def test_non_string_input_is_rejected():
    with pytest.raises(ValueError):
        create_co_definition("self-a", "self-b", None, "2026-09-21T00:00:00Z")


def test_result_is_immutable():
    item = create_co_definition("self-a", "self-b", "trust", "2026-09-21T00:00:00Z")

    with pytest.raises(FrozenInstanceError):
        item.left_id = "other"


def test_endpoint_order_is_structurally significant():
    forward = create_co_definition(
        "self-a", "self-b", "trust", "2026-09-21T00:00:00Z"
    )
    reverse = create_co_definition(
        "self-b", "self-a", "trust", "2026-09-21T00:00:00Z"
    )

    assert forward.id != reverse.id


def test_defining_changes_change_identity():
    base = create_co_definition(
        "self-a", "self-b", "trust", "2026-09-21T00:00:00Z"
    )

    assert create_co_definition(
        "self-a", "self-b", "support", "2026-09-21T00:00:00Z"
    ).id != base.id
    assert create_co_definition(
        "self-a", "self-c", "trust", "2026-09-21T00:00:00Z"
    ).id != base.id
    assert create_co_definition(
        "self-a", "self-b", "trust", "2026-09-22T00:00:00Z"
    ).id != base.id
