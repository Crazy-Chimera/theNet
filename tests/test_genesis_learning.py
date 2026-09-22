import pytest

from src.genesis_learning import simulate_genesis_learning
from src.genesis_population import create_genesis_population


def test_learning_can_progress_without_reputation_input():
    population = create_genesis_population(2, "2026-09-22T00:00:00Z")

    result = simulate_genesis_learning(
        population,
        (
            "learn proposal one",
            "learn proposal two",
            "learn proposal three",
        ),
        quorum=1,
        created_at=(
            "2026-09-22T00:00:01Z",
            "2026-09-22T00:00:02Z",
            "2026-09-22T00:00:03Z",
        ),
    )

    assert len(result.steps) == 3
    assert all(step.consensus_reached for step in result.steps)
    assert all(step.evolved for step in result.steps)
    assert result.final_state.version == 4


def test_learning_requires_an_independent_verifier():
    population = create_genesis_population(1, "2026-09-22T00:00:00Z")

    result = simulate_genesis_learning(
        population,
        ("cannot self-verify",),
        quorum=1,
        created_at=("2026-09-22T00:00:01Z",),
    )

    assert len(result.steps) == 1
    assert result.steps[0].verifier_count == 0
    assert result.steps[0].consensus_reached is False
    assert result.steps[0].evolved is False
    assert result.final_state == population.agents[0]


def test_failed_quorum_stops_subsequent_learning():
    population = create_genesis_population(2, "2026-09-22T00:00:00Z")

    result = simulate_genesis_learning(
        population,
        (
            "first proposal",
            "blocked second proposal",
        ),
        quorum=2,
        created_at=(
            "2026-09-22T00:00:01Z",
            "2026-09-22T00:00:02Z",
        ),
    )

    assert len(result.steps) == 1
    assert result.steps[0].consensus_reached is False
    assert result.final_state == population.agents[0]


def test_two_verifiers_allow_repeated_learning():
    population = create_genesis_population(3, "2026-09-22T00:00:00Z")

    result = simulate_genesis_learning(
        population,
        ("first", "second"),
        quorum=2,
        created_at=(
            "2026-09-22T00:00:01Z",
            "2026-09-22T00:00:02Z",
        ),
    )

    assert [step.verifier_count for step in result.steps] == [2, 2]
    assert [step.state_version for step in result.steps] == [2, 3]


def test_invalid_learning_inputs_are_rejected():
    population = create_genesis_population(2, "2026-09-22T00:00:00Z")

    with pytest.raises(ValueError):
        simulate_genesis_learning(
            population,
            (),
            quorum=1,
            created_at=(),
        )

    with pytest.raises(ValueError):
        simulate_genesis_learning(
            population,
            ("one",),
            quorum=1,
            created_at=(),
        )
