from dataclasses import FrozenInstanceError

import pytest

from src.rho import RelationalCoDefinition, create_rho


STAMP = "2026-09-22T14:00:00Z"


def test_create_rho():
    value = create_rho("self:a", "self:b", "co_define", STAMP)

    assert isinstance(value, RelationalCoDefinition)
    assert value.left_id == "self:a"
    assert value.right_id == "self:b"
    assert value.relation_kind == "co_define"
    assert value.created_at == STAMP
    assert value.version == 1
    assert len(value.id) == 64


def test_rho_is_deterministic():
    assert create_rho("self:a", "self:b", "co_define", STAMP) == create_rho(
        "self:a", "self:b", "co_define", STAMP
    )


@pytest.mark.parametrize(
    "values",
    [
        ("", "self:b", "co_define", STAMP),
        ("self:a", "", "co_define", STAMP),
        ("self:a", "self:b", "", STAMP),
        ("self:a", "self:b", "co_define", ""),
    ],
)
def test_empty_fields_are_rejected(values):
    with pytest.raises(ValueError):
        create_rho(*values)


def test_rho_is_directional():
    forward = create_rho("self:a", "self:b", "co_define", STAMP)
    reverse = create_rho("self:b", "self:a", "co_define", STAMP)

    assert forward.id != reverse.id


@pytest.mark.parametrize(
    "field_index",
    range(4),
)
def test_each_defining_input_changes_identity(field_index):
    base = ["self:a", "self:b", "co_define", STAMP]
    changed = base.copy()
    changed[field_index] += "-changed"

    assert create_rho(*base).id != create_rho(*changed).id


def test_rho_is_immutable():
    value = create_rho("self:a", "self:b", "co_define", STAMP)

    with pytest.raises(FrozenInstanceError):
        value.relation_kind = "other"


def test_inputs_are_not_mutated():
    values = ["self:a", "self:b", "co_define", STAMP]
    before = values.copy()

    create_rho(*values)

    assert values == before
