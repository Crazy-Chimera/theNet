import pytest
from src.genesis_network_bootstrap import bootstrap_three_agent_network
from src.network_runtime import NetworkRuntime

def bootstrap(tmp_path):
    return bootstrap_three_agent_network(
        vault_path=tmp_path/"vault", password="test-password",
        created_at="2026-09-30T00:00:00Z", proposal_text="F12 runtime proposal"
    )

def test_membership_persists_and_peer_discovery(tmp_path):
    boot=bootstrap(tmp_path); db=tmp_path/"runtime.db"
    runtime=NetworkRuntime(db,boot.network)
    for item in boot.agents: runtime.add_agent(item.admission.membership,item.agent)
    assert tuple(p.agent_id for p in runtime.active_members())==("agent-0","agent-1","agent-2")
    assert tuple(p.agent_id for p in runtime.discover_peers("agent-0"))==("agent-1","agent-2")
    reopened=NetworkRuntime(db,boot.network)
    assert tuple(p.agent_id for p in reopened.active_members())==("agent-0","agent-1","agent-2")

def test_handshake_session_persists_and_closes_on_remove(tmp_path):
    boot=bootstrap(tmp_path); runtime=NetworkRuntime(tmp_path/"runtime.db",boot.network)
    for item in boot.agents: runtime.add_agent(item.admission.membership,item.agent)
    session=runtime.register_handshake(boot.handshakes[0],created_at="2026-09-30T00:01:00Z")
    assert session.state=="established"
    runtime.remove_agent("agent-1")
    assert runtime.sessions()[0].state=="closed"

def test_snapshot_freezes_membership_and_derives_quorum(tmp_path):
    boot=bootstrap(tmp_path); runtime=NetworkRuntime(tmp_path/"runtime.db",boot.network)
    for item in boot.agents: runtime.add_agent(item.admission.membership,item.agent)
    snapshot=runtime.snapshot(created_at="2026-09-30T00:02:00Z")
    assert snapshot.members==("agent-0","agent-1","agent-2")
    assert snapshot.quorum==2
    runtime.remove_agent("agent-2")
    assert tuple(p.agent_id for p in runtime.active_members())==("agent-0","agent-1")
    assert runtime.get_snapshot(snapshot.snapshot_id)==snapshot
    runtime.validate_snapshot_verifiers(snapshot,"agent-0",("agent-1","agent-2"))

def test_new_snapshot_excludes_removed_agent(tmp_path):
    boot=bootstrap(tmp_path); runtime=NetworkRuntime(tmp_path/"runtime.db",boot.network)
    for item in boot.agents: runtime.add_agent(item.admission.membership,item.agent)
    runtime.remove_agent("agent-2")
    snapshot=runtime.snapshot(created_at="2026-09-30T00:03:00Z")
    assert snapshot.members==("agent-0","agent-1")
    assert snapshot.quorum==1

def test_session_heartbeat_and_reconnect(tmp_path):
    boot=bootstrap(tmp_path)
    runtime=NetworkRuntime(tmp_path/"runtime.db",boot.network)
    for item in boot.agents: runtime.add_agent(item.admission.membership,item.agent)
    session=runtime.register_handshake(boot.handshakes[0],created_at="2026-09-30T00:10:00Z")
    assert runtime.last_heartbeat(session.session_id) is None
    updated=runtime.heartbeat(session.session_id,seen_at="2026-09-30T00:11:00Z")
    assert updated.created_at=="2026-09-30T00:10:00Z"
    assert runtime.last_heartbeat(session.session_id)=="2026-09-30T00:11:00Z"

def test_stale_snapshot_can_be_detected_after_membership_change(tmp_path):
    boot=bootstrap(tmp_path)
    runtime=NetworkRuntime(tmp_path/"runtime.db",boot.network)
    for item in boot.agents: runtime.add_agent(item.admission.membership,item.agent)
    snapshot=runtime.snapshot(created_at="2026-09-30T00:12:00Z")
    runtime.remove_agent("agent-2")
    with pytest.raises(ValueError,match="stale"):
        runtime.validate_snapshot_current(snapshot)
