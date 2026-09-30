from dataclasses import FrozenInstanceError

import pytest

from src.agent_identity import (
    AgentIdentity,
    create_agent_identity,
    verify_agent_identity,
)
from src.genesis import create_genesis
from src.genesis_record import (
    create_genesis_record,
    verify_genesis_record,
)
from src.identity import IdentityVault
from src.network_identity import (
    create_network_identity,
    verify_network_identity,
)
from src.network_membership import (
    NetworkMembership,
    create_network_membership,
    verify_network_membership,
)
from src.resource_state import create_resource_state


def _bootstrap(tmp_path):
    vault = IdentityVault(tmp_path / "vault.json")
    identity = vault.create("genesis-password")
    genesis = create_genesis("agent:genesis", "2026-09-30T00:00:00Z")
    resource = create_resource_state(100.0, 0.0, "2026-09-30T00:00:00Z")
    record = create_genesis_record(
        genesis,
        identity,
        "initial-state",
        resource,
        capability_manifest=("proposal", "verification"),
        invariant_set=("immutable-state", "consensus-before-mutation"),
    )
    agent = create_agent_identity(record, identity)
    network = create_network_identity(record.genesis_id)
    membership = create_network_membership(network, agent)
    return genesis, identity, resource, record, agent, network, membership


def test_f11_genesis_record_is_deterministic(tmp_path):
    vault = IdentityVault(tmp_path / "vault.json")
    identity = vault.create("genesis-password")
    genesis = create_genesis("agent:genesis", "2026-09-30T00:00:00Z")
    resource = create_resource_state(100.0, 0.0, "2026-09-30T00:00:00Z")
    first = create_genesis_record(
        genesis,
        identity,
        "initial-state",
        resource,
        capability_manifest=("proposal", "verification"),
        invariant_set=("immutable-state", "consensus-before-mutation"),
    )
    second = create_genesis_record(
        genesis,
        identity,
        "initial-state",
        resource,
        capability_manifest=("proposal", "verification"),
        invariant_set=("immutable-state", "consensus-before-mutation"),
    )
    assert first == second


def test_f11_genesis_record_verifies(tmp_path):
    genesis, identity, resource, record, *_ = _bootstrap(tmp_path)
    assert verify_genesis_record(record, genesis, identity, resource)


def test_f11_agent_identity_binds_to_genesis(tmp_path):
    *_, record, agent, _, _ = _bootstrap(tmp_path)
    assert isinstance(agent, AgentIdentity)
    assert agent.genesis_id == record.genesis_id
    assert verify_agent_identity(
        agent,
        record,
        IdentityVault(tmp_path / "vault.json").get(agent.identity_did),
    )


def test_f11_agent_identity_rejects_wrong_identity(tmp_path):
    genesis, identity, resource, record, *_ = _bootstrap(tmp_path)
    other_vault = IdentityVault(tmp_path / "other-vault.json")
    other_identity = other_vault.create("other-password")
    other_record = create_genesis_record(
        genesis,
        other_identity,
        record.initial_state_id,
        resource,
    )
    with pytest.raises(ValueError, match="identity does not match"):
        create_agent_identity(other_record, identity)


def test_f11_network_identity_is_deterministic(tmp_path):
    *_, record, _, network, _ = _bootstrap(tmp_path)
    assert network == create_network_identity(record.genesis_id)
    assert verify_network_identity(network, record.genesis_id)


def test_f11_membership_binds_agent_and_network(tmp_path):
    *_, record, agent, network, membership = _bootstrap(tmp_path)
    assert isinstance(membership, NetworkMembership)
    assert membership.network_id == network.network_id
    assert membership.agent_id == agent.agent_id
    assert verify_network_membership(membership, network, agent)


def test_f11_membership_rejects_cross_genesis(tmp_path):
    *_, agent, _, _, membership = _bootstrap(tmp_path)
    other_network = create_network_identity("different-genesis")
    with pytest.raises(ValueError, match="Genesis"):
        create_network_membership(other_network, agent)


def test_f11_artifacts_are_immutable(tmp_path):
    *_, record, agent, network, membership = _bootstrap(tmp_path)
    with pytest.raises(FrozenInstanceError):
        record.genesis_id = "changed"
    with pytest.raises(FrozenInstanceError):
        agent.agent_id = "changed"
    with pytest.raises(FrozenInstanceError):
        network.network_id = "changed"
    with pytest.raises(FrozenInstanceError):
        membership.agent_id = "changed"
