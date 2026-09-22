import pytest

from src.genesis_learning import simulate_genesis_learning
from src.genesis_majority_learning import simulate_genesis_majority_learning
from src.genesis_population import create_genesis_population


@pytest.mark.parametrize(
    ("population_size", "expected_quorum", "expected_verifiers"),
    [
        (2, 1, 1),
        (3, 2, 2),
        (4, 2, 3),
        (5, 3, 4),
    ],
)
def test_majority_bootstrap_scales_with_independent_verifiers(
    population_size,
    expected_quorum,
    expected_verifiers,
):
    population = create_genesis_population(
        population_size,
        "2026-09-22T00:00:00Z",
    )

    result = simulate_genesis_majority_learning(
        population,
        ("bootstrap",),
        ("2026-09-22T00:00:01Z",),
    )

    step = result.steps[0]

    assert step.quorum == expected_quorum
    assert step.verifier_count == expected_verifiers
    assert step.consensus_reached is True
    assert step.evolved is True


def test_single_agent_can_propose_but_cannot_collectively_evolve():
    population = create_genesis_population(
        1,
        "2026-09-22T00:00:00Z",
    )

    with pytest.raises(ValueError, match="independent verifier"):
        simulate_genesis_majority_learning(
            population,
            ("bootstrap",),
            ("2026-09-22T00:00:01Z",),
        )


def test_failed_explicit_quorum_preserves_state():
    population = create_genesis_population(
        2,
        "2026-09-22T00:00:00Z",
    )

    result = simulate_genesis_learning(
        population,
        ("blocked",),
        quorum=2,
        created_at=("2026-09-22T00:00:01Z",),
    )

    assert result.steps[0].consensus_reached is False
    assert result.steps[0].evolved is False
    assert result.final_state == population.agents[0]
