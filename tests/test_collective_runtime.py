from __future__ import annotations

import pytest

from src.agent_state import create_agent_state
from src.collective_runtime import run_collective_computation
from src.genesis import create_genesis
from src.proposal import create_proposal
from src.resource_state import create_resource_state
from src.verification import create_verification


STAMP = "2026-09-30T05:00:00Z"


def _inputs(quorum: int = 2):
    agent = create_genesis("agent-a", STAMP)
    verifier_b = create_genesis("agent-b", STAMP)
    verifier_c = create_genesis("agent-c", STAMP)
    state = create_agent_state(agent.id, "singularity-a", STAMP)
    proposal = create_proposal(
        agent.id,
        state.id,
        "collectively execute verified computation",
        STAMP,
    )
    verifications = (
        create_verification(proposal.id, verifier_b.id, "evidence-b", True, STAMP),
        create_verification(proposal.id, verifier_c.id, "evidence-c", True, STAMP),
    )
    return (
        state,
        proposal,
        verifications,
        create_resource_state(100.0, 0.0, STAMP),
        create_resource_state(100.0, 0.0, STAMP),
    )


def _run():
    state, proposal, verifications, memory, compute = _inputs()
    return run_collective_computation(
        state,
        proposal,
        verifications,
        quorum=2,
        new_singularity_id="singularity-b",
        created_at=STAMP,
        memory_resource=memory,
        compute_resource=compute,
        executor=lambda item: f"executed:{item.proposal}",
    )


def test_runtime_closes_collective_computation_loop():
    result = _run()

    assert result.consensus.reached is True
    assert result.convergence.converged is True
    assert result.outcome.success is True
    assert result.outcome.proposal_id == result.commit.proposal_id
    assert result.memory.source_id == result.outcome.id
    assert result.utility.verified is True
    assert result.utility.evidence_ids == tuple(sorted((result.memory.id, result.outcome.id)))
    assert result.credit.verified is True
    assert result.credit.credit > 0.0
    assert result.contribution_ledger.entries == (result.credit.id,)
    assert result.execution.contribution_ledger_id == result.contribution_ledger.id
    assert result.execution.memory_after_id == result.memory_resource.id
    assert result.execution.compute_after_id == result.compute_resource.id
    assert result.state.version == 2
    assert result.metrics.k > 0.8
    assert result.metrics.c < 0.3
    assert result.metrics.r > 5
    assert result.metrics.phi > 0.7
    assert result.metrics.converged is True


def test_runtime_is_deterministic():
    assert _run() == _run()


def test_runtime_requires_quorum_before_execution():
    state, proposal, verifications, memory, compute = _inputs()
    called = False

    def executor(_proposal):
        nonlocal called
        called = True
        return "should not run"

    with pytest.raises(ValueError, match="quorum"):
        run_collective_computation(
            state,
            proposal,
            verifications[:1],
            quorum=2,
            new_singularity_id="singularity-b",
            created_at=STAMP,
            memory_resource=memory,
            compute_resource=compute,
            executor=executor,
        )

    assert called is False


def test_runtime_does_not_advance_state_when_executor_fails():
    state, proposal, verifications, memory, compute = _inputs()

    def executor(_proposal):
        raise RuntimeError("sandbox failure")

    with pytest.raises(RuntimeError, match="sandbox failure"):
        run_collective_computation(
            state,
            proposal,
            verifications,
            quorum=2,
            new_singularity_id="singularity-b",
            created_at=STAMP,
            memory_resource=memory,
            compute_resource=compute,
            executor=executor,
        )

    assert state.version == 1
    assert memory.used == 0.0
    assert compute.used == 0.0


def test_runtime_rejects_non_string_execution_result():
    state, proposal, verifications, memory, compute = _inputs()

    with pytest.raises(TypeError, match="string result"):
        run_collective_computation(
            state,
            proposal,
            verifications,
            quorum=2,
            new_singularity_id="singularity-b",
            created_at=STAMP,
            memory_resource=memory,
            compute_resource=compute,
            executor=lambda _proposal: 42,
        )


def test_runtime_rejects_replayed_commit():
    first = _run()
    state, proposal, verifications, memory, compute = _inputs()

    with pytest.raises(ValueError, match="already been applied"):
        run_collective_computation(
            state,
            proposal,
            verifications,
            quorum=2,
            new_singularity_id="singularity-b",
            created_at=STAMP,
            memory_resource=memory,
            compute_resource=compute,
            executor=lambda item: f"executed:{item.proposal}",
            prior_commits=(first.commit,),
        )
