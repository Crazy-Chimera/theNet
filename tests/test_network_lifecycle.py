from src.network_lifecycle import run_network_lifecycle_mvp


def test_network_lifecycle_mvp_completes_end_to_end(tmp_path):
    result = run_network_lifecycle_mvp(
        database=tmp_path / "runtime.db",
        vault_path=tmp_path / "vault",
        password="test-password",
        created_at="2026-09-30T02:00:00Z",
        proposal_text="advance network state",
    )
    assert result.version == "3.0.0-mvp"
    assert result.phases == (
        "GENESIS",
        "ADMISSION",
        "MEMBERSHIP",
        "PEER_DISCOVERY",
        "HANDSHAKE",
        "SESSION",
        "SNAPSHOT",
        "WORK_ANNOUNCEMENT",
        "VERIFICATION",
        "QUORUM",
        "COORDINATION",
        "EXECUTION",
        "OUTCOME",
    )
    assert len(result.active_agents) == 3
    assert result.snapshot["quorum"] == 2
    assert result.coordination["verifier_ids"] == ("agent-1", "agent-2")
    assert result.outcome["outcome_id"]
    assert result.outcome["credit_id"]


def test_network_lifecycle_service_persists_membership_and_snapshot_epoch(tmp_path):
    from src.network_lifecycle import NetworkLifecycleService

    service = NetworkLifecycleService(
        database=tmp_path / "runtime.db",
        vault_path=tmp_path / "vault",
        password="test-password",
        created_at="2026-09-30T03:00:00Z",
        proposal_text="bootstrap",
    )
    first = service.run(
        created_at="2026-09-30T03:00:01Z",
        proposal_text="first computation",
    )
    assert first.snapshot["quorum"] == 2
    assert len(service.runtime.active_members()) == 3

    service.remove_agent("agent-2")
    second = service.snapshot(created_at="2026-09-30T03:00:02Z")
    assert second.epoch > first.snapshot["epoch"]
    assert second.members == ("agent-0", "agent-1")
    assert second.quorum == 1

    from src.network_runtime import NetworkRuntime

    reopened = NetworkRuntime(
        tmp_path / "runtime.db",
        service.bootstrap.network,
        created_at="2026-09-30T04:00:00Z",
    )
    persisted = reopened.get_snapshot(second.snapshot_id)
    assert persisted == second
