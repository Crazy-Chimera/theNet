"""Immutable Agent Ω identity binding over the existing Ed25519 identity."""
from __future__ import annotations
from dataclasses import dataclass
from src.genesis_record import GenesisRecord
from src.identity import Identity

@dataclass(frozen=True)
class AgentIdentity:
    agent_id: str
    identity_did: str
    genesis_id: str
    public_key: str
    network_genesis_id: str | None = None
    version: int = 1

def create_agent_identity(genesis_record: GenesisRecord, identity: Identity) -> AgentIdentity:
    if not isinstance(genesis_record, GenesisRecord): raise TypeError("genesis_record must be GenesisRecord")
    if not isinstance(identity, Identity): raise TypeError("identity must be Identity")
    if identity.did != genesis_record.identity_did: raise ValueError("identity does not match GenesisRecord")
    return AgentIdentity(genesis_record.agent_id,identity.did,genesis_record.genesis_id,identity.public_key,genesis_record.network_genesis_id)

def verify_agent_identity(agent_identity: AgentIdentity, genesis_record: GenesisRecord, identity: Identity) -> bool:
    if not isinstance(agent_identity, AgentIdentity): raise TypeError("agent_identity must be AgentIdentity")
    if not isinstance(genesis_record, GenesisRecord): raise TypeError("genesis_record must be GenesisRecord")
    if not isinstance(identity, Identity): raise TypeError("identity must be Identity")
    return (agent_identity.agent_id==genesis_record.agent_id and agent_identity.genesis_id==genesis_record.genesis_id and agent_identity.identity_did==identity.did and agent_identity.public_key==identity.public_key and agent_identity.network_genesis_id==genesis_record.network_genesis_id)

__all__=["AgentIdentity","create_agent_identity","verify_agent_identity"]
