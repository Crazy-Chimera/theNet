import pytest

from src.genesis_verification_gate import (
    GenesisVerificationGate,
    evaluate_genesis_verification,
)


def test_single_agent_cannot_approve_collective_verification():
    gate = evaluate_genesis_verification(1, 0)

    assert isinstance(gate, GenesisVerificationGate)
    assert gate.approved is False
    assert gate.reputation_required is False


def test_two_agents_enable_first_independent_verification():
    gate = evaluate_genesis_verification(2, 1)

    assert gate.approved is True
    assert gate.verifier_count == 1
    assert gate.required_quorum == 1


def test_quorum_is_explicit():
    assert evaluate_genesis_verification(3, 1, 2).approved is False
    assert evaluate_genesis_verification(3, 2, 2).approved is True


def test_proposer_is_not_counted_as_verifier():
    with pytest.raises(ValueError):
        evaluate_genesis_verification(2, 2)


@pytest.mark.parametrize("population_size", [0, -1, True, 1.5])
def test_invalid_population_is_rejected(population_size):
    with pytest.raises(ValueError):
        evaluate_genesis_verification(population_size, 0)


@pytest.mark.parametrize("verifier_count", [-1, True, 1.5])
def test_invalid_verifier_count_is_rejected(verifier_count):
    with pytest.raises(ValueError):
        evaluate_genesis_verification(2, verifier_count)


@pytest.mark.parametrize("required_quorum", [0, -1, True, 1.5])
def test_invalid_quorum_is_rejected(required_quorum):
    with pytest.raises(ValueError):
        evaluate_genesis_verification(2, 1, required_quorum)


def test_gate_is_immutable_and_deterministic():
    first = evaluate_genesis_verification(4, 2, 2)
    second = evaluate_genesis_verification(4, 2, 2)

    assert first == second
    with pytest.raises(AttributeError):
        first.approved = False
