from dataclasses import FrozenInstanceError

import pytest

from src.execution_chain import ExecutionChain, create_execution_chain
from src.execution_ledger import create_execution_record


STAMP = "2026-09-22T00:00:00Z"


def make_record(
    suffix: str,
    memory_before: str,
    memory_after: str,
    compute_before: str,
    compute_after: str,
):
    return create_execution_record(
        contribution_ledger_id=f"ledger-{suffix}",
        allocation_id=f"allocation-{suffix}",
        memory_before_id=memory_before,
        memory_after_id=memory_after,
        compute_before_id=compute_before,
        compute_after_id=compute_after,
        memory_by_contributor=(("alice", 1.0),),
        compute_by_contributor=(("alice", 1.0),),
        created_at=f"2026-09-22T12:0{suffix}:00Z",
    )


def test_single_record_is_continuous():
    record = make_record("1", "m0", "m1", "c0", "c1")
    chain = create_execution_chain([record])

    assert isinstance(chain, ExecutionChain)
    assert chain.continuous is True
    assert chain.records == (record,)


def test_adjacent_resource_boundaries_are_continuous():
    first = make_record("1", "m0", "m1", "c0", "c1")
    second = make_record("2", "m1", "m2", "c1", "c2")

    chain = create_execution_chain([first, second])

    assert chain.continuous is True


def test_broken_memory_boundary_is_not_continuous():
    first = make_record("1", "m0", "m1", "c0", "c1")
    second = make_record("2", "other", "m2", "c1", "c2")

    assert create_execution_chain([first, second]).continuous is False


def test_broken_compute_boundary_is_not_continuous():
    first = make_record("1", "m0", "m1", "c0", "c1")
    second = make_record("2", "m1", "m2", "other", "c2")

    assert create_execution_chain([first, second]).continuous is False


def test_empty_chain_is_valid():
    chain = create_execution_chain([])

    assert chain.records == ()
    assert chain.continuous is True


def test_order_is_semantic():
    first = make_record("1", "m0", "m1", "c0", "c1")
    second = make_record("2", "m1", "m2", "c1", "c2")

    assert create_execution_chain([first, second]).id != create_execution_chain([second, first]).id


def test_invalid_record_is_rejected():
    with pytest.raises(TypeError, match="ExecutionRecord"):
        create_execution_chain([object()])


def test_chain_is_immutable():
    record = make_record("1", "m0", "m1", "c0", "c1")
    chain = create_execution_chain([record])

    with pytest.raises(FrozenInstanceError):
        chain.continuous = False
