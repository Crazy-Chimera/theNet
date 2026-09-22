from __future__ import annotations

import pytest

from src.agent_state import create_agent_state
from src.collective_evolution import evolve_collectively
from src.genesis import create_genesis
from src.omega_credit import create_omega_credit
from src.omega_credit_allocation import create_omega_credit_allocation
from src.omega_credit_engine import create_omega_credit_distribution_from_ledger
from src.proposal import create_proposal
from src.verification import create_verification
from src.contribution_ledger import create_contribution_ledger


STAMP = "2026-09-22T17:45:00Z"


def test_verified_evolution_persists_contribution_before_allocation():
    proposer = create_genesis("agent-a", STAMP)
    verifier = create_genesis("agent-b", STAMP)
    state = create_agent_state(proposer.id, "singularity-a", STAMP)

    proposal = create_proposal(
        proposer.id,
        state.id,
        "verified collective learning",
        STAMP,
    )
    verification = create_verification(
        proposal.id,
        verifier.id,
        "evidence-b",
        True,
        STAMP,
    )

    evolution = evolve_collectively(
        state,
        proposal,
        [verification],
        quorum=1,
        new_singularity_id="singularity-b",
        created_at=STAMP,
    )

    first = create_omega_credit(
        proposer.id, 0.8, 0.9, 1.0, True, STAMP
    )
    second = create_omega_credit(
        proposer.id, 0.4, 0.5, 1.0, True, "2026-09-22T17:46:00Z"
    )
    verifier_credit = create_omega_credit(
        verifier.id, 0.5, 1.0, 1.0, True, STAMP
    )

    ledger = create_contribution_ledger(
        [verifier_credit, second, first]
    )
    distribution = create_omega_credit_distribution_from_ledger(ledger)
    allocation = create_omega_credit_allocation(
        distribution,
        memory_capacity=100.0,
        compute_capacity=50.0,
    )

    assert evolution.commit.id in {
        evolution.commit.id
    }
    assert ledger.totals[0][0] == proposer.id
    assert distribution.total_credit == pytest.approx(
        first.credit + second.credit + verifier_credit.credit
    )
    assert sum(share for _, _, share in distribution.contributions) == pytest.approx(1.0)
    assert sum(value for _, value in allocation.memory_by_contributor) == pytest.approx(100.0)
    assert sum(value for _, value in allocation.compute_by_contributor) == pytest.approx(50.0)
