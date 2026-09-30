"""F11.7-F11.8 multi-agent Genesis network bootstrap."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from src.agent_identity import AgentIdentity,create_agent_identity
from src.agent_state import AgentState,create_agent_state
from src.collective_runtime import CollectiveComputationResult,run_collective_computation
from src.genesis import GenesisState,create_genesis
from src.genesis_record import GenesisRecord,create_genesis_record
from src.identity import Identity,IdentityVault
from src.network_admission import AdmissionResult,admit_agent,create_admission_challenge,create_admission_request
from src.network_handshake import Handshake,complete_handshake,create_handshake_transcript
from src.network_identity import NetworkIdentity,create_network_identity
from src.proposal import create_proposal
from src.resource_state import ResourceState,create_resource_state
from src.verification import create_verification
@dataclass(frozen=True)
class BootstrappedAgent:
    identity:Identity; genesis:GenesisRecord; agent:AgentIdentity; state:AgentState; resource:ResourceState; admission:AdmissionResult
@dataclass(frozen=True)
class GenesisNetworkBootstrap:
    root_genesis:GenesisState; network:NetworkIdentity; agents:tuple[BootstrappedAgent,...]; handshakes:tuple[Handshake,...]; collective_result:CollectiveComputationResult
def bootstrap_three_agent_network(*,vault_path:str|Path,password:str,created_at:str,proposal_text:str)->GenesisNetworkBootstrap:
    if not isinstance(password,str) or not password: raise ValueError("password must be non-empty")
    if not isinstance(proposal_text,str) or not proposal_text.strip(): raise ValueError("proposal_text must be non-empty")
    vault=IdentityVault(vault_path); root=create_genesis("thenet:genesis-root",created_at); network=create_network_identity(root.id); agents=[]
    for index in range(3):
        identity=vault.create(password); resource=create_resource_state(100.0,0.0,created_at)
        record=create_genesis_record(root,identity,f"genesis-state:{identity.did}",resource,agent_id=f"agent-{index}",capability_manifest=("proposal","verification","collective-compute"),invariant_set=("immutable-genesis","consensus-before-mutation"),network_genesis_id=root.id)
        agent=create_agent_identity(record,identity); state=create_agent_state(agent.agent_id,f"iota:{agent.agent_id}",created_at); nonce=f"admission:{index}"
        challenge=create_admission_challenge(network,agent,nonce); signature=vault.sign(identity.did,challenge,password); request=create_admission_request(network,agent,identity,signature,nonce); admission=admit_agent(request,network,agent,record,identity)
        if not admission.admitted: raise ValueError(f"agent admission failed: {admission.reason}")
        agents.append(BootstrappedAgent(identity,record,agent,state,resource,admission))
    handshakes=[]
    for index in (1,2):
        left,right=agents[0],agents[index]; nonce=f"handshake:{index}"; transcript=create_handshake_transcript(network,left.agent,right.agent,nonce)
        handshakes.append(complete_handshake(network,left.agent,right.agent,left.identity,right.identity,vault.sign(left.identity.did,transcript,password),vault.sign(right.identity.did,transcript,password),nonce))
    proposer=agents[0]; proposal=create_proposal(proposer.state.subject_id,proposer.state.id,proposal_text,created_at)
    verifications=tuple(create_verification(proposal.id,a.state.subject_id,f"handshake-verified:{a.agent.agent_identity_id}",True,created_at) for a in agents[1:])
    result=run_collective_computation(proposer.state,proposal,verifications,2,f"iota:collective:{proposal.id}",created_at,create_resource_state(100.0,0.0,created_at),create_resource_state(100.0,0.0,created_at),lambda p:f"genesis-collective:{p.id}")
    return GenesisNetworkBootstrap(root,network,tuple(agents),tuple(handshakes),result)
__all__=["BootstrappedAgent","GenesisNetworkBootstrap","bootstrap_three_agent_network"]
