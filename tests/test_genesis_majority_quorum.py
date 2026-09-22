import pytest

from src.genesis_majority_quorum import genesis_majority_quorum


def test_genesis_majority_quorum_excludes_proposer():
    assert genesis_majority_quorum(2) == 1
    assert genesis_majority_quorum(3) == 2
    assert genesis_majority_quorum(4) == 2
    assert genesis_majority_quorum(5) == 3


def test_single_agent_genesis_cannot_reach_collective_quorum():
    with pytest.raises(ValueError):
        genesis_majority_quorum(1)


def test_invalid_population_is_rejected():
    with pytest.raises(ValueError):
        genesis_majority_quorum(0)

    with pytest.raises(ValueError):
        genesis_majority_quorum(True)
