import pytest

from src.genesis_population import (
    create_genesis_population,
    simulate_genesis_proposal,
)


def test_population_is_deterministic_and_distinct():
    first = create_genesis_population(3, "2026-09-22T00:00:00Z")
    second = create_genesis_population(3, "2026-09-22T00:00:00Z")

    assert first == second
    assert len({agent.subject_id for agent in first.agents}) == 3
    assert len({agent.id for agent in first.agents}) == 3


def test_quorum_one_allows_single_verifier():
    population = create_genesis_population(2, "2026-09-22T00:00:00Z")

    result = simulate_genesis_proposal(
        population,
        "evolve through verified proposal",
        quorum=1,
        created_at="2026-09-22T00:00:01Z",
    )

    assert result.quorum_reached is True
    assert result.evolution is not None
    assert result.evolution.consensus.quorum == 1
    assert result.evolution.consensus.verifier_ids == (
        population.agents[1].subject_id,
    )
    assert result.evolution.state.version == 2


def test_quorum_two_requires_two_distinct_verifiers():
    population = create_genesis_population(3, "2026-09-22T00:00:00Z")

    result = simulate_genesis_proposal(
        population,
        "evolve through collective verification",
        quorum=2,
        created_at="2026-09-22T00:00:01Z",
    )

    assert result.quorum_reached is True
    assert result.evolution is not None
    assert len(result.evolution.consensus.verifier_ids) == 2


def test_unreachable_quorum_blocks_evolution_without_mutation():
    population = create_genesis_population(3, "2026-09-22T00:00:00Z")
    proposer_before = population.agents[0]

    result = simulate_genesis_proposal(
        population,
        "proposal without enough verifiers",
        quorum=3,
        created_at="2026-09-22T00:00:01Z",
    )

    assert result.quorum_reached is False
    assert result.evolution is None
    assert population.agents[0] == proposer_before


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        create_genesis_population(0, "2026-09-22T00:00:00Z")

    population = create_genesis_population(2, "2026-09-22T00:00:00Z")

    with pytest.raises(ValueError):
        simulate_genesis_proposal(
            population,
            "",
            quorum=1,
            created_at="2026-09-22T00:00:01Z",
        )
