"""Immutable GenesisRecord bootstrap artifact for Agent Ω."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from src.genesis import GenesisState
from src.identity import Identity
from src.resource_state import ResourceState

@dataclass(frozen=True)
class GenesisRecord:
    genesis_id: str
    agent_id: str
    identity_did: str
    initial_state_id: str
    capability_manifest: tuple[str, ...]
    invariant_set: tuple[str, ...]
    memory_root: str | None
    resource_state_id: str
    created_at: str
    network_genesis_id: str | None = None
    version: int = 1

def create_genesis_record(genesis: GenesisState, identity: Identity, initial_state_id: str, resource_state: ResourceState, *, agent_id: str | None = None, capability_manifest: tuple[str, ...] | list[str] = (), invariant_set: tuple[str, ...] | list[str] = (), memory_root: str | None = None, network_genesis_id: str | None = None) -> GenesisRecord:
    if not isinstance(genesis, GenesisState): raise TypeError("genesis must be GenesisState")
    if not isinstance(identity, Identity): raise TypeError("identity must be Identity")
    if not isinstance(resource_state, ResourceState): raise TypeError("resource_state must be ResourceState")
    if not isinstance(initial_state_id, str) or not initial_state_id.strip(): raise ValueError("initial_state_id must be non-empty")
    if memory_root is not None and (not isinstance(memory_root, str) or not memory_root.strip()): raise ValueError("memory_root must be non-empty when provided")
    if network_genesis_id is not None and (not isinstance(network_genesis_id, str) or not network_genesis_id.strip()): raise ValueError("network_genesis_id must be non-empty when provided")
    normalized_agent_id = agent_id or identity.did
    if not isinstance(normalized_agent_id, str) or not normalized_agent_id.strip(): raise ValueError("agent_id must be non-empty")
    capabilities, invariants = tuple(capability_manifest), tuple(invariant_set)
    if any(not isinstance(v, str) or not v.strip() for v in capabilities): raise ValueError("capability_manifest must contain non-empty strings")
    if any(not isinstance(v, str) or not v.strip() for v in invariants): raise ValueError("invariant_set must contain non-empty strings")
    payload={"agent_id":normalized_agent_id,"capability_manifest":capabilities,"created_at":genesis.created_at,"genesis_id":genesis.id,"identity_did":identity.did,"initial_state_id":initial_state_id,"invariant_set":invariants,"memory_root":memory_root,"resource_state_id":resource_state.id,"version":1}
    if network_genesis_id is not None: payload["network_genesis_id"]=network_genesis_id
    return GenesisRecord(sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest(),normalized_agent_id,identity.did,initial_state_id,capabilities,invariants,memory_root,resource_state.id,genesis.created_at,network_genesis_id)

def verify_genesis_record(record: GenesisRecord, genesis: GenesisState, identity: Identity, resource_state: ResourceState) -> bool:
    if not all(isinstance(value, expected) for value,expected in ((record,GenesisRecord),(genesis,GenesisState),(identity,Identity),(resource_state,ResourceState))): raise TypeError("invalid GenesisRecord verification inputs")
    return create_genesis_record(genesis,identity,record.initial_state_id,resource_state,agent_id=record.agent_id,capability_manifest=record.capability_manifest,invariant_set=record.invariant_set,memory_root=record.memory_root,network_genesis_id=record.network_genesis_id)==record

__all__=["GenesisRecord","create_genesis_record","verify_genesis_record"]
