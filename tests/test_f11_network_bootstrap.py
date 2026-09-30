from pathlib import Path
import pytest
from src.genesis_network_bootstrap import bootstrap_three_agent_network
from src.network_admission import create_admission_challenge
from src.network_handshake import create_handshake_transcript
def test_f11_5_admission_and_f11_6_handshake(tmp_path:Path):
    run=bootstrap_three_agent_network(vault_path=tmp_path/"vault.json",password="bootstrap-password",created_at="2026-09-30T00:00:00Z",proposal_text="first collective computation")
    assert len(run.agents)==3 and all(a.admission.admitted for a in run.agents)
    assert len(run.handshakes)==2 and all(h.network_id==run.network.network_id for h in run.handshakes)
def test_f11_7_shared_genesis_network_anchor(tmp_path:Path):
    run=bootstrap_three_agent_network(vault_path=tmp_path/"vault.json",password="bootstrap-password",created_at="2026-09-30T00:00:00Z",proposal_text="shared genesis")
    assert len({a.genesis.genesis_id for a in run.agents})==3
    assert all(a.genesis.network_genesis_id==run.root_genesis.id for a in run.agents)
    assert all(a.admission.membership.network_id==run.network.network_id for a in run.agents)
def test_f11_8_three_agent_collective_computation(tmp_path:Path):
    run=bootstrap_three_agent_network(vault_path=tmp_path/"vault.json",password="bootstrap-password",created_at="2026-09-30T00:00:00Z",proposal_text="first three agent computation")
    assert run.collective_result.consensus.reached and len(run.collective_result.consensus.verification_ids)==2
    assert run.collective_result.outcome.success and run.collective_result.state.id!=run.agents[0].state.id
def test_handshake_rejects_same_agent(tmp_path:Path):
    run=bootstrap_three_agent_network(vault_path=tmp_path/"vault.json",password="bootstrap-password",created_at="2026-09-30T00:00:00Z",proposal_text="handshake")
    with pytest.raises(ValueError,match="distinct"): create_handshake_transcript(run.network,run.agents[0].agent,run.agents[0].agent,"same")
def test_admission_challenge_is_deterministic(tmp_path:Path):
    run=bootstrap_three_agent_network(vault_path=tmp_path/"vault.json",password="bootstrap-password",created_at="2026-09-30T00:00:00Z",proposal_text="challenge")
    assert create_admission_challenge(run.network,run.agents[0].agent,"nonce")==create_admission_challenge(run.network,run.agents[0].agent,"nonce")
