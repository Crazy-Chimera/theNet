import pytest

from src.genesis_bootstrap_policy import derive_genesis_bootstrap_policy


@pytest.mark.parametrize(
    ("population_size", "verifiers", "quorum"),
    [
        (2, 1, 1),
        (3, 2, 2),
        (4, 3, 2),
        (5, 4, 3),
    ],
)
def test_bootstrap_policy_derives_majority_from_population(
    population_size,
    verifiers,
    quorum,
):
    policy = derive_genesis_bootstrap_policy(population_size)

    assert policy.population_size == population_size
    assert policy.proposer_count == 1
    assert policy.eligible_verifier_count == verifiers
    assert policy.quorum == quorum
    assert policy.collective_learning_possible is True


def test_single_agent_has_no_collective_learning_path():
    policy = derive_genesis_bootstrap_policy(1)

    assert policy.eligible_verifier_count == 0
    assert policy.quorum == 0
    assert policy.collective_learning_possible is False


@pytest.mark.parametrize("population_size", [0, -1, True, 1.5])
def test_invalid_population_size_is_rejected(population_size):
    with pytest.raises(ValueError):
        derive_genesis_bootstrap_policy(population_size)


def test_policy_is_immutable():
    policy = derive_genesis_bootstrap_policy(3)

    with pytest.raises(AttributeError):
        policy.quorum = 1
