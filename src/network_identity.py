"""Immutable identity for a theNet network."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class NetworkIdentity:
    network_id: str
    genesis_id: str
    protocol_version: int = 1
    version: int = 1


def create_network_identity(
    genesis_id: str,
    *,
    protocol_version: int = 1,
) -> NetworkIdentity:
    if not isinstance(genesis_id, str) or not genesis_id.strip():
        raise ValueError("genesis_id must be non-empty")
    if isinstance(protocol_version, bool) or not isinstance(protocol_version, int):
        raise ValueError("protocol_version must be an integer")
    if protocol_version < 1:
        raise ValueError("protocol_version must be positive")

    canonical = json.dumps(
        {
            "genesis_id": genesis_id,
            "protocol_version": protocol_version,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    network_id = sha256(canonical.encode("utf-8")).hexdigest()

    return NetworkIdentity(
        network_id=network_id,
        genesis_id=genesis_id,
        protocol_version=protocol_version,
    )


def verify_network_identity(
    network: NetworkIdentity,
    genesis_id: str,
) -> bool:
    if not isinstance(network, NetworkIdentity):
        raise TypeError("network must be NetworkIdentity")
    if not isinstance(genesis_id, str) or not genesis_id.strip():
        raise ValueError("genesis_id must be non-empty")

    return network == create_network_identity(
        genesis_id,
        protocol_version=network.protocol_version,
    )


__all__ = ["NetworkIdentity", "create_network_identity", "verify_network_identity"]
