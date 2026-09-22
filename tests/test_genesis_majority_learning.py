import pytest

from src.genesis_majority_learning import simulate_genesis_majority_learning
from src.genesis_population import create_genesis_population


def test_majority_learning_derives_quorum_from_population():
    population = create_genesis_population(3, "2026-09-22T00:00:00Z")

    result = simulate_genesis_majority_learning(
        population,
        ("first", "second"),
        (
            "2026-09-22T00:00:01Z",
            "2026-09-22T00:00:02Z",
        ),
    )

    assert [step.quorum for step in result.steps] == [2, 2]
    assert [step.verifier_count for step in result.steps] == [2, 2]
    assert result.final_state.version == 3


def test_two_agents_need_one_independent_verifier():
    population = create_genesis_population(2, "2026-09-22T00:00:00Z")

    result = simulate_genesis_majority_learning(
        population,
        ("first",),
        ("2026-09-22T00:00:01Z",),
    )

    assert result.steps[0].quorum == 1
    assert result.steps[0].consensus_reached is True
    assert result.final_state.version == 2


def test_single_agent_cannot_use_majority_learning_without_verifier():
    population = create_genesis_population(1, "2026-09-22T00:00:00Z")

    with pytest.raises(ValueError, match="independent verifier"):
        simulate_genesis_majority_learning(
            population,
            ("cannot self-verify",),
            ("2026-09-22T00:00:01Z",),
        )
