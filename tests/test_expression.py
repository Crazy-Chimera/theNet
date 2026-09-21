from dataclasses import FrozenInstanceError

import pytest

from src.expression import create_expression


def test_expression_creation():
    expression = create_expression(
        "meaning-1",
        "action-1",
        "2026-09-21T00:03:00Z",
    )

    assert expression.meaning_id == "meaning-1"
    assert expression.expression_id == "action-1"
    assert expression.created_at == "2026-09-21T00:03:00Z"
    assert expression.version == 1
    assert len(expression.id) == 64


def test_expression_is_deterministic():
    first = create_expression("meaning-1", "action-1", "2026-09-21T00:03:00Z")
    second = create_expression("meaning-1", "action-1", "2026-09-21T00:03:00Z")

    assert first == second


@pytest.mark.parametrize(
    "meaning_id, expression_id, created_at",
    [
        ("", "action", "2026-09-21T00:03:00Z"),
        ("meaning", "", "2026-09-21T00:03:00Z"),
        ("meaning", "action", ""),
        (None, "action", "2026-09-21T00:03:00Z"),
    ],
)
def test_expression_rejects_invalid_inputs(
    meaning_id,
    expression_id,
    created_at,
):
    with pytest.raises(ValueError):
        create_expression(meaning_id, expression_id, created_at)


def test_expression_changes_when_meaning_changes():
    first = create_expression("meaning-1", "action-1", "2026-09-21T00:03:00Z")
    second = create_expression("meaning-2", "action-1", "2026-09-21T00:03:00Z")

    assert first.id != second.id


def test_expression_changes_when_expression_changes():
    first = create_expression("meaning-1", "action-1", "2026-09-21T00:03:00Z")
    second = create_expression("meaning-1", "action-2", "2026-09-21T00:03:00Z")

    assert first.id != second.id


def test_expression_is_immutable():
    expression = create_expression("meaning-1", "action-1", "2026-09-21T00:03:00Z")

    with pytest.raises(FrozenInstanceError):
        expression.expression_id = "changed"
