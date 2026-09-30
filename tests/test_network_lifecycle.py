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


def test_network_lifecycle_run_does_not_rejoin_removed_agent(tmp_path):
    from src.network_lifecycle import NetworkLifecycleService

    service = NetworkLifecycleService(
        database=tmp_path / "runtime.db",
        vault_path=tmp_path / "vault",
        password="test-password",
        created_at="2026-09-30T05:00:00Z",
        proposal_text="bootstrap",
    )
    service.run(
        created_at="2026-09-30T05:00:01Z",
        proposal_text="initial computation",
    )
    service.remove_agent("agent-2")

    result = service.run(
        created_at="2026-09-30T05:00:02Z",
        proposal_text="post-leave computation",
    )
    assert result.active_agents == ("agent-0", "agent-1")
    assert result.snapshot["members"] == ("agent-0", "agent-1")
    assert result.snapshot["quorum"] == 1

    service.add_agent("agent-2")
    joined = service.snapshot(created_at="2026-09-30T05:00:03Z")
    assert joined.members == ("agent-0", "agent-1", "agent-2")
    assert joined.quorum == 2


def test_removed_agent_is_excluded_from_next_computation_snapshot(tmp_path):
    from src.network_lifecycle import NetworkLifecycleService

    service = NetworkLifecycleService(
        database=tmp_path / "runtime.db",
        vault_path=tmp_path / "vault",
        password="test-password",
        created_at="2026-09-30T05:00:00Z",
        proposal_text="bootstrap",
    )
    first = service.run(
        created_at="2026-09-30T05:00:01Z",
        proposal_text="before leave",
    )
    service.remove_agent("agent-2")

    second = service.run(
        created_at="2026-09-30T05:00:02Z",
        proposal_text="after leave",
    )

    assert first.snapshot["members"] == ("agent-0", "agent-1", "agent-2")
    assert first.snapshot["quorum"] == 2
    assert second.snapshot["members"] == ("agent-0", "agent-1")
    assert second.snapshot["quorum"] == 1
    assert second.active_agents == ("agent-0", "agent-1")
    assert second.coordination["verifier_ids"] == ("agent-1",)
    assert first.snapshot["snapshot_id"] != second.snapshot["snapshot_id"]

def test_network_lifecycle_service_preserves_removed_membership_after_process_restart(tmp_path):
    from src.network_lifecycle import NetworkLifecycleService

    db = tmp_path / "runtime.db"
    vault = tmp_path / "vault"
    first_service = NetworkLifecycleService(
        database=db,
        vault_path=vault,
        password="test-password",
        created_at="2026-09-30T06:00:00Z",
        proposal_text="bootstrap",
    )
    first_service.remove_agent("agent-2")

    restarted_service = NetworkLifecycleService(
        database=db,
        vault_path=vault,
        password="test-password",
        created_at="2026-09-30T06:00:01Z",
        proposal_text="restart",
    )

    assert tuple(item.agent_id for item in restarted_service.runtime.active_members()) == (
        "agent-0",
        "agent-1",
    )
    snapshot = restarted_service.snapshot(created_at="2026-09-30T06:00:02Z")
    assert snapshot.members == ("agent-0", "agent-1")
    assert snapshot.quorum == 1
