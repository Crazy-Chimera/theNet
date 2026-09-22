from src.genesis_bootstrap_policy import derive_genesis_bootstrap_policy


def test_bootstrap_population_matrix_matches_independent_verifier_capacity():
    expected = (
        (1, 0, 0, False),
        (2, 1, 1, True),
        (3, 2, 2, True),
        (4, 3, 2, True),
        (5, 4, 3, True),
    )

    for population_size, verifiers, quorum, possible in expected:
        policy = derive_genesis_bootstrap_policy(population_size)

        assert policy.eligible_verifier_count == verifiers
        assert policy.quorum == quorum
        assert policy.collective_learning_possible is possible


def test_bootstrap_quorum_never_exceeds_available_verifiers():
    for population_size in range(2, 21):
        policy = derive_genesis_bootstrap_policy(population_size)

        assert policy.quorum <= policy.eligible_verifier_count
        assert policy.quorum >= 1
