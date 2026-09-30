import pytest
from src.genesis_network_bootstrap import bootstrap_three_agent_network
from src.network_coordination import (
    create_coordination_record,
    create_work_announcement,
    verify_coordination_record,
    verify_work_announcement,
)
from src.network_runtime import NetworkRuntime
from src.proposal import create_proposal
from src.verification import create_verification


def bootstrap(tmp_path):
    return bootstrap_three_agent_network(
        vault_path=tmp_path / "vault",
        password="test-password",
        created_at="2026-09-30T01:00:00Z",
        proposal_text="F13 coordination proposal",
    )


def prepare(tmp_path):
    boot = bootstrap(tmp_path)
    runtime = NetworkRuntime(tmp_path / "runtime.db", boot.network)
    for item in boot.agents:
        runtime.add_agent(item.admission.membership, item.agent)
    snapshot = runtime.snapshot(created_at="2026-09-30T01:01:00Z")
    proposal = create_proposal(
        boot.agents[0].state.subject_id,
        boot.agents[0].state.id,
        "F13 coordinated work",
        "2026-09-30T01:02:00Z",
    )
    verifications = tuple(
        create_verification(
            proposal.id,
            item.state.subject_id,
            f"verified:{item.agent.agent_id}",
            True,
            "2026-09-30T01:02:00Z",
        )
        for item in boot.agents[1:]
    )
    return boot, runtime, snapshot, proposal, verifications


def test_work_announcement_is_bound_to_snapshot_and_proposal(tmp_path):
    boot, runtime, snapshot, proposal, _ = prepare(tmp_path)
    announcement = create_work_announcement(snapshot, proposal)
    assert announcement.network_id == boot.network.network_id
    assert announcement.epoch == snapshot.epoch
    assert verify_work_announcement(announcement, snapshot, proposal)
    runtime.remove_agent("agent-2")
    assert verify_work_announcement(announcement, snapshot, proposal)


def test_coordination_record_is_deterministic_and_quorum_bound(tmp_path):
    _, _, snapshot, proposal, verifications = prepare(tmp_path)
    first = create_coordination_record(snapshot, proposal, verifications)
    second = create_coordination_record(snapshot, proposal, verifications)
    assert first == second
    assert first.verifier_ids == ("agent-1", "agent-2")
    assert first.quorum == 2
    assert verify_coordination_record(first, snapshot, proposal)


def test_coordination_rejects_insufficient_quorum(tmp_path):
    _, _, snapshot, proposal, verifications = prepare(tmp_path)
    with pytest.raises(ValueError, match="quorum"):
        create_coordination_record(snapshot, proposal, verifications[:1])


def test_coordination_rejects_verifier_outside_snapshot(tmp_path):
    _, _, snapshot, proposal, verifications = prepare(tmp_path)
    forged = create_verification(
        proposal.id, "agent-9", "forged", True, "2026-09-30T01:02:00Z"
    )
    with pytest.raises(ValueError, match="not in membership snapshot"):
        create_coordination_record(snapshot, proposal, (*verifications[:1], forged))


def test_coordination_record_detects_different_proposal(tmp_path):
    _, _, snapshot, proposal, verifications = prepare(tmp_path)
    record = create_coordination_record(snapshot, proposal, verifications)
    other = create_proposal(
        proposal.proposer_id,
        proposal.base_state_id,
        "different work",
        proposal.created_at,
    )
    assert not verify_coordination_record(record, snapshot, other)
