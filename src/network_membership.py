"""Immutable Agent Ω membership in a network."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from src.agent_identity import AgentIdentity
from src.network_identity import NetworkIdentity


@dataclass(frozen=True)
class NetworkMembership:
    membership_id: str
    network_id: str
    agent_id: str
    genesis_id: str
    role: str
    status: str
    version: int = 1


def create_network_membership(
    network: NetworkIdentity,
    agent: AgentIdentity,
    *,
    role: str = "agent",
    status: str = "active",
) -> NetworkMembership:
    if not isinstance(network, NetworkIdentity):
        raise TypeError("network must be NetworkIdentity")
    if not isinstance(agent, AgentIdentity):
        raise TypeError("agent must be AgentIdentity")
    if network.genesis_id != agent.genesis_id:
        raise ValueError("agent Genesis does not match network Genesis")
    if not isinstance(role, str) or not role.strip():
        raise ValueError("role must be non-empty")
    if not isinstance(status, str) or not status.strip():
        raise ValueError("status must be non-empty")

    canonical = json.dumps(
        {
            "agent_id": agent.agent_id,
            "genesis_id": agent.genesis_id,
            "network_id": network.network_id,
            "role": role,
            "status": status,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    membership_id = sha256(canonical.encode("utf-8")).hexdigest()

    return NetworkMembership(
        membership_id=membership_id,
        network_id=network.network_id,
        agent_id=agent.agent_id,
        genesis_id=agent.genesis_id,
        role=role,
        status=status,
    )


def verify_network_membership(
    membership: NetworkMembership,
    network: NetworkIdentity,
    agent: AgentIdentity,
) -> bool:
    if not isinstance(membership, NetworkMembership):
        raise TypeError("membership must be NetworkMembership")
    if not isinstance(network, NetworkIdentity):
        raise TypeError("network must be NetworkIdentity")
    if not isinstance(agent, AgentIdentity):
        raise TypeError("agent must be AgentIdentity")

    try:
        expected = create_network_membership(
            network,
            agent,
            role=membership.role,
            status=membership.status,
        )
    except ValueError:
        return False
    return expected == membership


__all__ = [
    "NetworkMembership",
    "create_network_membership",
    "verify_network_membership",
]
