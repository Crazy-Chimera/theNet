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
