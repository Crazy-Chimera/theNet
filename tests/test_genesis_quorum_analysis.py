from dataclasses import FrozenInstanceError

import pytest

from src.genesis_quorum_analysis import (
    GenesisQuorumAnalysis,
    analyze_genesis_quorum,
)


def test_analysis_excludes_proposer_from_available_verifiers():
    result = analyze_genesis_quorum(4, 4)

    assert isinstance(result, GenesisQuorumAnalysis)
    assert result.available_verifiers == 3
    assert [row.reachable for row in result.rows] == [True, True, True, False]


def test_required_population_is_quorum_plus_proposer():
    result = analyze_genesis_quorum(10, 3)

    assert [row.required_population for row in result.rows] == [2, 3, 4]


def test_analysis_is_deterministic():
    assert analyze_genesis_quorum(5, 5) == analyze_genesis_quorum(5, 5)


def test_population_of_one_has_no_reachable_positive_quorum():
    result = analyze_genesis_quorum(1, 2)

    assert result.available_verifiers == 0
    assert all(not row.reachable for row in result.rows)


def test_invalid_population_is_rejected():
    with pytest.raises(ValueError):
        analyze_genesis_quorum(0, 1)

    with pytest.raises(ValueError):
        analyze_genesis_quorum(True, 1)


def test_invalid_max_quorum_is_rejected():
    with pytest.raises(ValueError):
        analyze_genesis_quorum(2, 0)

    with pytest.raises(ValueError):
        analyze_genesis_quorum(2, False)


def test_analysis_is_immutable():
    result = analyze_genesis_quorum(3, 2)

    with pytest.raises(FrozenInstanceError):
        result.population_size = 4
