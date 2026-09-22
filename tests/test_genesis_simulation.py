import pytest

from src.genesis import create_genesis
from src.genesis_simulation import GenesisSimulation, simulate_genesis_proposal
from thenet.engine import simulate_genesis_agents


STAMP = "2026-09-22T00:00:00Z"


def test_genesis_simulation_reaches_explicit_quorum():
    result = simulate_genesis_proposal(
        population_size=4,
        quorum=2,
        proposal_text="learn verified relation",
        created_at=STAMP,
    )

    assert isinstance(result, GenesisSimulation)
    assert result.proposer_id == create_genesis("agent-1", STAMP).id
    assert len(result.verifier_ids) == 2
    assert len(set(result.verifier_ids)) == 2
    assert result.committed_version == result.initial_version + 1
    assert result.initial_state_id != result.committed_state_id


def test_genesis_simulation_excludes_proposer():
    result = simulate_genesis_proposal(4, 2, "proposal", STAMP)

    assert result.proposer_id not in result.verifier_ids


def test_genesis_simulation_requires_reachable_quorum():
    with pytest.raises(ValueError, match="verifier_count"):
        simulate_genesis_proposal(2, 2, "proposal", STAMP)


def test_genesis_simulation_is_deterministic():
    first = simulate_genesis_proposal(4, 2, "proposal", STAMP)
    second = simulate_genesis_proposal(4, 2, "proposal", STAMP)

    assert first == second


def test_genesis_simulation_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        simulate_genesis_proposal(0, 1, "proposal", STAMP)

    with pytest.raises(ValueError):
        simulate_genesis_proposal(2, 0, "proposal", STAMP)

    with pytest.raises(ValueError):
        simulate_genesis_proposal(3, 1, "", STAMP)


def test_runtime_facade_exposes_same_simulation():
    direct = simulate_genesis_proposal(3, 1, "proposal", STAMP)
    facade = simulate_genesis_agents(3, 1, "proposal", STAMP)

    assert facade == direct

def test_genesis_simulation_matches_bootstrap_gate_boundary():
    from src.genesis_verification_gate import evaluate_genesis_verification

    gate = evaluate_genesis_verification(3, 2, 2)

    assert gate.approved is True
    result = simulate_genesis_proposal(3, 2, "proposal", STAMP)
    assert len(result.verifier_ids) == gate.verifier_count
