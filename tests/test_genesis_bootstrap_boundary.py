import pytest

from src.genesis_bootstrap_boundary import (
    GenesisBootstrapBoundary,
    derive_genesis_bootstrap_boundary,
)


@pytest.mark.parametrize(
    ("population_size", "verifiers", "quorum"),
    [
        (1, 0, 0),
        (2, 1, 1),
        (3, 2, 1),
        (5, 4, 1),
    ],
)
def test_bootstrap_boundary_is_explicit(
    population_size,
    verifiers,
    quorum,
):
    boundary = derive_genesis_bootstrap_boundary(population_size)

    assert isinstance(boundary, GenesisBootstrapBoundary)
    assert boundary.population_size == population_size
    assert boundary.eligible_verifier_count == verifiers
    assert boundary.minimum_quorum == quorum
    assert boundary.reputation_required is False
    assert boundary.collective_learning_possible is (population_size >= 2)


def test_single_agent_cannot_bootstrap_collective_learning():
    boundary = derive_genesis_bootstrap_boundary(1)

    assert boundary.eligible_verifier_count == 0
    assert boundary.minimum_quorum == 0
    assert boundary.collective_learning_possible is False


def test_two_agents_are_the_minimum_for_first_independent_verification():
    boundary = derive_genesis_bootstrap_boundary(2)

    assert boundary.eligible_verifier_count == 1
    assert boundary.minimum_quorum == 1
    assert boundary.collective_learning_possible is True


@pytest.mark.parametrize("population_size", [0, -1, True, 1.5])
def test_invalid_population_size_is_rejected(population_size):
    with pytest.raises(ValueError):
        derive_genesis_bootstrap_boundary(population_size)


def test_bootstrap_boundary_is_immutable():
    boundary = derive_genesis_bootstrap_boundary(2)

    with pytest.raises(AttributeError):
        boundary.minimum_quorum = 2


def test_bootstrap_boundary_is_deterministic():
    assert derive_genesis_bootstrap_boundary(4) == derive_genesis_bootstrap_boundary(4)
