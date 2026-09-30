import pytest
from src.genesis_network_bootstrap import bootstrap_three_agent_network
from src.network_runtime import NetworkRuntime
from src.peer_announcement import create_peer_announcement, verify_peer_announcement
from src.identity import IdentityVault

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


def test_handshake_replay_is_rejected(tmp_path):
    boot=bootstrap(tmp_path)
    runtime=NetworkRuntime(tmp_path/"runtime.db",boot.network)
    for item in boot.agents: runtime.add_agent(item.admission.membership,item.agent)
    runtime.register_handshake(boot.handshakes[0],created_at="2026-09-30T00:20:00Z")
    with pytest.raises(ValueError,match="replay"):
        runtime.register_handshake(boot.handshakes[0],created_at="2026-09-30T00:21:00Z")


def test_membership_epoch_has_audit_events(tmp_path):
    boot=bootstrap(tmp_path)
    runtime=NetworkRuntime(tmp_path/"runtime.db",boot.network)
    for item in boot.agents: runtime.add_agent(item.admission.membership,item.agent)
    events=runtime.membership_events()
    assert len(events)==3
    assert tuple(e[1] for e in events)==(1,2,3)
    runtime.remove_agent("agent-2")
    events=runtime.membership_events()
    assert events[-1][1]==4
    assert events[-1][2:4]==("agent-2","leave")


def test_lifecycle_and_active_discovery_guard(tmp_path):
    boot=bootstrap(tmp_path)
    runtime=NetworkRuntime(tmp_path/"runtime.db",boot.network)
    for item in boot.agents: runtime.add_agent(item.admission.membership,item.agent)
    assert runtime.lifecycle("agent-0").state=="ACTIVE"
    runtime.remove_agent("agent-2")
    assert runtime.lifecycle("agent-2").state=="REMOVED"
    with pytest.raises(ValueError,match="active agent"):
        runtime.discover_peers("agent-2")


def test_signed_peer_announcement_binds_identity_and_epoch(tmp_path):
    boot=bootstrap(tmp_path)
    runtime=NetworkRuntime(tmp_path/"runtime.db",boot.network)
    for item in boot.agents: runtime.add_agent(item.admission.membership,item.agent)
    identity=boot.agents[0].identity
    message='{"agent_id":"agent-0","epoch":3,"identity_did":"'+identity.did+'","network_id":"'+boot.network.network_id+'","status":"active","version":1}'
    signature=IdentityVault(tmp_path/"vault").sign(identity.did,message,"test-password")
    announcement=create_peer_announcement(boot.network,boot.agents[0].agent,identity,3,"active",signature)
    assert verify_peer_announcement(announcement,boot.network,boot.agents[0].agent,identity)
    assert not verify_peer_announcement(announcement,boot.network,boot.agents[1].agent,boot.agents[1].identity)


def test_fresh_snapshot_guard_rejects_membership_change(tmp_path):
    boot=bootstrap(tmp_path)
    runtime=NetworkRuntime(tmp_path/"runtime.db",boot.network)
    for item in boot.agents: runtime.add_agent(item.admission.membership,item.agent)
    snapshot=runtime.snapshot(created_at="2026-09-30T00:30:00Z")
    runtime.remove_agent("agent-2")
    with pytest.raises(ValueError,match="stale"):
        runtime.validate_snapshot_current(snapshot)
