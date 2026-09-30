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
    version: int = 1


def _canonical(
    genesis_id: str,
    agent_id: str,
    identity_did: str,
    initial_state_id: str,
    capability_manifest: tuple[str, ...],
    invariant_set: tuple[str, ...],
    memory_root: str | None,
    resource_state_id: str,
    created_at: str,
) -> str:
    return json.dumps(
        {
            "agent_id": agent_id,
            "capability_manifest": capability_manifest,
            "created_at": created_at,
            "genesis_id": genesis_id,
            "identity_did": identity_did,
            "initial_state_id": initial_state_id,
            "invariant_set": invariant_set,
            "memory_root": memory_root,
            "resource_state_id": resource_state_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_genesis_record(
    genesis: GenesisState,
    identity: Identity,
    initial_state_id: str,
    resource_state: ResourceState,
    *,
    agent_id: str | None = None,
    capability_manifest: tuple[str, ...] | list[str] = (),
    invariant_set: tuple[str, ...] | list[str] = (),
    memory_root: str | None = None,
) -> GenesisRecord:
    if not isinstance(genesis, GenesisState):
        raise TypeError("genesis must be GenesisState")
    if not isinstance(identity, Identity):
        raise TypeError("identity must be Identity")
    if not isinstance(resource_state, ResourceState):
        raise TypeError("resource_state must be ResourceState")
    if not isinstance(initial_state_id, str) or not initial_state_id.strip():
        raise ValueError("initial_state_id must be non-empty")
    if memory_root is not None and (not isinstance(memory_root, str) or not memory_root.strip()):
        raise ValueError("memory_root must be non-empty when provided")

    normalized_agent_id = agent_id or identity.did
    if not isinstance(normalized_agent_id, str) or not normalized_agent_id.strip():
        raise ValueError("agent_id must be non-empty")

    capabilities = tuple(capability_manifest)
    invariants = tuple(invariant_set)
    if any(not isinstance(v, str) or not v.strip() for v in capabilities):
        raise ValueError("capability_manifest must contain non-empty strings")
    if any(not isinstance(v, str) or not v.strip() for v in invariants):
        raise ValueError("invariant_set must contain non-empty strings")

    canonical = _canonical(
        genesis.id,
        normalized_agent_id,
        identity.did,
        initial_state_id,
        capabilities,
        invariants,
        memory_root,
        resource_state.id,
        genesis.created_at,
    )
    genesis_id = sha256(canonical.encode("utf-8")).hexdigest()

    return GenesisRecord(
        genesis_id=genesis_id,
        agent_id=normalized_agent_id,
        identity_did=identity.did,
        initial_state_id=initial_state_id,
        capability_manifest=capabilities,
        invariant_set=invariants,
        memory_root=memory_root,
        resource_state_id=resource_state.id,
        created_at=genesis.created_at,
    )


def verify_genesis_record(
    record: GenesisRecord,
    genesis: GenesisState,
    identity: Identity,
    resource_state: ResourceState,
) -> bool:
    if not all(
        isinstance(value, expected)
        for value, expected in (
            (record, GenesisRecord),
            (genesis, GenesisState),
            (identity, Identity),
            (resource_state, ResourceState),
        )
    ):
        raise TypeError("invalid GenesisRecord verification inputs")
    expected = create_genesis_record(
        genesis,
        identity,
        record.initial_state_id,
        resource_state,
        agent_id=record.agent_id,
        capability_manifest=record.capability_manifest,
        invariant_set=record.invariant_set,
        memory_root=record.memory_root,
    )
    return expected == record


__all__ = ["GenesisRecord", "create_genesis_record", "verify_genesis_record"]
