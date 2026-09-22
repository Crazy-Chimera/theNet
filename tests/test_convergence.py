from dataclasses import FrozenInstanceError
import pytest
from src.convergence import Convergence, create_convergence

STAMP = "2026-09-22T00:06:00Z"

def test_create():
    value = create_convergence(["b", "a"], "a", STAMP)
    assert isinstance(value, Convergence)
    assert value.candidate_states == ("a", "b")
    assert value.selected_state == "a"
    assert len(value.id) == 64

def test_order_and_duplicates():
    assert create_convergence(["b", "a", "a"], "a", STAMP) == create_convergence(["a", "b"], "a", STAMP)

def test_empty_candidates():
    with pytest.raises(ValueError):
        create_convergence([], "a", STAMP)

def test_invalid_candidate():
    with pytest.raises(ValueError):
        create_convergence(["a", ""], "a", STAMP)

def test_selection_must_exist():
    with pytest.raises(ValueError):
        create_convergence(["a", "b"], "c", STAMP)

def test_required_fields():
    with pytest.raises(ValueError):
        create_convergence(["a"], "", STAMP)
    with pytest.raises(ValueError):
        create_convergence(["a"], "a", "")

def test_changes_affect_identity():
    base = create_convergence(["a", "b"], "a", STAMP)
    assert base.id != create_convergence(["a", "b", "c"], "a", STAMP).id
    assert base.id != create_convergence(["a", "b"], "b", STAMP).id

def test_immutable():
    value = create_convergence(["a"], "a", STAMP)
    with pytest.raises(FrozenInstanceError):
        value.selected_state = "b"

def test_input_not_mutated():
    candidates = ["b", "a", "a"]
    create_convergence(candidates, "a", STAMP)
    assert candidates == ["b", "a", "a"]
