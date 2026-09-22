from dataclasses import FrozenInstanceError

import pytest

from src.resource_state import create_resource_state


def test_resource_state_normalizes_efficiency():
    state = create_resource_state(100.0, 40.0, "2026-09-22T06:20:00Z")

    assert state.available == 100.0
    assert state.used == 40.0
    assert state.efficiency == pytest.approx(0.4)
    assert len(state.id) == 64


def test_efficiency_is_capped_at_one():
    state = create_resource_state(10.0, 20.0, "now")

    assert state.efficiency == 1.0


def test_zero_capacity_has_zero_efficiency():
    state = create_resource_state(0.0, 0.0, "now")

    assert state.efficiency == 0.0


def test_resource_state_is_deterministic():
    left = create_resource_state(10, 5, "now")
    right = create_resource_state(10.0, 5.0, "now")

    assert left == right


@pytest.mark.parametrize("name", ["available", "used"])
def test_negative_resources_are_rejected(name):
    values = {"available": 1.0, "used": 1.0, "created_at": "now"}
    values[name] = -1.0

    with pytest.raises(ValueError):
        create_resource_state(**values)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_resources_are_rejected(value):
    with pytest.raises(ValueError):
        create_resource_state(value, 0.0, "now")


def test_created_at_is_required():
    with pytest.raises(ValueError):
        create_resource_state(1.0, 0.0, "")


def test_result_is_immutable():
    state = create_resource_state(1.0, 0.5, "now")

    with pytest.raises(FrozenInstanceError):
        state.efficiency = 0.0
