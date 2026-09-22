import pytest

from src.omega_allocation import allocate_credit
from src.omega_credit import create_omega_credit


def credit(agent, value, verified=True):
    return create_omega_credit(
        agent,
        value,
        1.0,
        1.0,
        verified,
        f"2026-09-22T06:0{len(agent)}:00Z",
    )


def test_allocates_capacity_proportionally():
    first = credit("agent-a", 0.2)
    second = credit("agent-b", 0.8)

    result = allocate_credit([first, second], 100.0)

    assert result[0].contributor_id == "agent-a"
    assert result[1].contributor_id == "agent-b"
    assert result[0].allocation == pytest.approx(20.0)
    assert result[1].allocation == pytest.approx(80.0)
    assert sum(item.allocation for item in result) == pytest.approx(100.0)


def test_aggregates_multiple_credits_for_one_contributor():
    result = allocate_credit(
        [credit("agent-a", 0.2), credit("agent-a", 0.3), credit("agent-b", 0.5)],
        10.0,
    )

    assert [(item.contributor_id, item.credit) for item in result] == [
        ("agent-a", pytest.approx(0.5)),
        ("agent-b", pytest.approx(0.5)),
    ]
    assert [item.allocation for item in result] == [
        pytest.approx(5.0),
        pytest.approx(5.0),
    ]


def test_unverified_credit_does_not_receive_allocation():
    result = allocate_credit(
        [credit("agent-a", 0.9, verified=False), credit("agent-b", 0.1)],
        10.0,
    )

    assert result == (
        result[0],
    )
    assert result[0].contributor_id == "agent-b"
    assert result[0].allocation == pytest.approx(10.0)


def test_zero_positive_credit_returns_zero_allocations():
    result = allocate_credit([credit("agent-a", 0.0)], 10.0)

    assert result == ()


@pytest.mark.parametrize("capacity", [-1.0, float("inf"), float("nan")])
def test_invalid_capacity_is_rejected(capacity):
    with pytest.raises(ValueError):
        allocate_credit([], capacity)


def test_non_credit_input_is_rejected():
    with pytest.raises(ValueError):
        allocate_credit([object()], 1.0)


def test_empty_input_does_not_allocate():
    assert allocate_credit([], 10.0) == ()


def test_input_is_not_mutated():
    items = [credit("agent-a", 0.5)]
    original = list(items)

    allocate_credit(items, 10.0)

    assert items == original
