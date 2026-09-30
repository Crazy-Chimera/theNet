import pytest

from src.timechain import (
    Timechain,
    commit_branch,
    create_branch,
    create_timechain,
    merge_branches,
    predict_state,
    rollback_branch,
)


STAMP = "2026-09-30T00:00:00Z"


def test_timechain_starts_at_genesis():
    chain = create_timechain("s0")

    assert isinstance(chain, Timechain)
    assert chain.genesis_state_id == "s0"
    assert chain.branches == ()


def test_branch_commit_and_rollback():
    chain = create_timechain("s0")
    branch = create_branch(chain, "main")
    committed = commit_branch(branch, "s1", "decision", STAMP)
    rolled_back = rollback_branch(committed, "s0", STAMP)

    assert committed.current_state_id == "s1"
    assert committed.state_history == ("s0", "s1")
    assert rolled_back.current_state_id == "s0"
    assert rolled_back.events[-1].kind == "ROLLBACK"


def test_branching_from_shared_state():
    chain = create_timechain("s0")
    main = commit_branch(create_branch(chain, "main"), "s1", "main", STAMP)
    left = create_branch(chain, "left", "s1")
    right = create_branch(chain, "right", "s1")

    assert left.base_state_id == right.base_state_id == "s1"


def test_prediction_is_recorded_without_mutating_state():
    chain = create_timechain("s0")
    branch = create_branch(chain, "main")
    prediction = predict_state(branch, "future", "expected convergence", STAMP)

    assert prediction.kind == "PREDICTION"
    assert prediction.parent_state_id == "s0"
    assert prediction.state_id == "future"
    assert branch.current_state_id == "s0"


def test_merge_requires_shared_base():
    chain = create_timechain("s0")
    left = create_branch(chain, "left")
    right = create_branch(chain, "right")
    left = commit_branch(left, "s1", "left", STAMP)
    right = commit_branch(right, "s2", "right", STAMP)

    merged = merge_branches(left, right, "s3", STAMP)

    assert merged.current_state_id == "s3"
    assert merged.events[-1].kind == "MERGE"
    assert "s1" in merged.state_history
    assert "s2" in merged.state_history


def test_merge_rejects_different_bases():
    chain = create_timechain("s0")
    left = create_branch(chain, "left")
    other_chain = create_timechain("other")
    right = create_branch(other_chain, "right")

    with pytest.raises(ValueError, match="shared base"):
        merge_branches(left, right, "s3", STAMP)


def test_invalid_rollback_target_is_rejected():
    branch = create_branch(create_timechain("s0"), "main")

    with pytest.raises(ValueError, match="rollback target"):
        rollback_branch(branch, "missing", STAMP)


def test_timechain_objects_are_immutable():
    branch = create_branch(create_timechain("s0"), "main")

    with pytest.raises((AttributeError, TypeError)):
        branch.current_state_id = "s1"
