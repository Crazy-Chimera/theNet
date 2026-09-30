"""theNet 3.0 end-to-end lifecycle MVP."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from src.genesis_network_bootstrap import GenesisNetworkBootstrap, bootstrap_three_agent_network
from src.network_coordination import (
    CoordinationRecord,
    WorkAnnouncement,
    create_coordination_record,
    create_work_announcement,
    run_coordinated_snapshot_computation,
)
from src.network_runtime import MembershipSnapshot, NetworkRuntime
from src.verification import Verification, create_verification
from src.resource_state import create_resource_state
from src.proposal import Proposal, create_proposal


@dataclass(frozen=True)
class NetworkLifecycleResult:
    version: str
    phases: tuple[str, ...]
    network_id: str
    epoch: int
    active_agents: tuple[str, ...]
    peer_counts: dict[str, int]
    sessions: tuple[dict[str, Any], ...]
    snapshot: dict[str, Any]
    announcement: dict[str, Any]
    coordination: dict[str, Any]
    outcome: dict[str, Any]


def _snapshot(snapshot: MembershipSnapshot) -> dict[str, Any]:
    return asdict(snapshot)


def _record(record: CoordinationRecord | WorkAnnouncement) -> dict[str, Any]:
    return asdict(record)


def run_network_lifecycle_mvp(
    *,
    database: str | Path,
    vault_path: str | Path,
    password: str,
    created_at: str,
    proposal_text: str,
    executor: Callable[[Proposal], str] | None = None,
    bootstrap: GenesisNetworkBootstrap | None = None,
    runtime: NetworkRuntime | None = None,
) -> NetworkLifecycleResult:
    boot = bootstrap or bootstrap_three_agent_network(
        vault_path=vault_path,
        password=password,
        created_at=created_at,
        proposal_text=proposal_text,
    )
    live_runtime = runtime or NetworkRuntime(database, boot.network, created_at=created_at)
    runtime = live_runtime

    phases: list[str] = ["GENESIS", "ADMISSION"]
    for item in boot.agents:
        runtime.add_agent(item.admission.membership, item.agent)

    phases.append("MEMBERSHIP")
    peers = {
        item.agent.agent_id: len(runtime.discover_peers(item.agent.agent_id))
        for item in boot.agents
    }
    phases.append("PEER_DISCOVERY")

    for handshake in boot.handshakes:
        runtime.register_handshake(handshake, created_at=created_at)
    phases.append("HANDSHAKE")
    phases.append("SESSION")

    snapshot = runtime.snapshot(created_at=created_at)
    phases.append("SNAPSHOT")

    proposer = boot.agents[0]
    proposal = create_proposal(
        proposer.state.subject_id,
        proposer.state.id,
        proposal_text,
        created_at,
    )
    verifications: tuple[Verification, ...] = tuple(
        create_verification(
            proposal.id,
            item.agent.agent_id,
            f"snapshot-verified:{snapshot.snapshot_id}",
            True,
            created_at,
        )
        for item in boot.agents[1:]
    )
    announcement = create_work_announcement(snapshot, proposal)
    phases.append("WORK_ANNOUNCEMENT")

    memory = create_resource_state(100.0, 0.0, created_at)
    compute = create_resource_state(100.0, 0.0, created_at)
    coordination, result = run_coordinated_snapshot_computation(
        runtime=runtime,
        snapshot=snapshot,
        current_state=proposer.state,
        proposal=proposal,
        verifications=verifications,
        created_at=created_at,
        memory_resource=memory,
        compute_resource=compute,
        executor=executor or (lambda item: f"executed:{item.id}"),
    )
    phases.extend(["VERIFICATION", "QUORUM", "COORDINATION", "EXECUTION", "OUTCOME"])

    return NetworkLifecycleResult(
        version="3.0.0-mvp",
        phases=tuple(phases),
        network_id=boot.network.network_id,
        epoch=snapshot.epoch,
        active_agents=tuple(item.agent.agent_id for item in boot.agents),
        peer_counts=peers,
        sessions=tuple(asdict(session) for session in runtime.sessions()),
        snapshot=_snapshot(snapshot),
        announcement=_record(announcement),
        coordination=_record(coordination),
        outcome={
            "outcome_id": result.outcome.id,
            "execution_id": result.execution.id,
            "utility_id": result.utility.id,
            "credit_id": result.credit.id,
            "memory_id": result.memory.id,
            "state_id": result.state.id,
            "utility": result.outcome.utility,
            "omega_credit": result.credit.credit,
        },
    )


class NetworkLifecycleService:
    """Process-persistent F12 runtime boundary for theNet 3.0 MVP."""

    def __init__(self, *, database: str | Path, vault_path: str | Path, password: str, created_at: str, proposal_text: str):
        self.database = str(database)
        self.vault_path = str(vault_path)
        self.password = password
        self.created_at = created_at
        self.bootstrap = bootstrap_three_agent_network(
            vault_path=vault_path,
            password=password,
            created_at=created_at,
            proposal_text=proposal_text,
        )
        self.runtime = NetworkRuntime(database, self.bootstrap.network, created_at=created_at)
        for item in self.bootstrap.agents:
            self.runtime.add_agent(item.admission.membership, item.agent)
        for handshake in self.bootstrap.handshakes:
            try:
                self.runtime.register_handshake(handshake, created_at=created_at)
            except ValueError as exc:
                if "replay" not in str(exc):
                    raise

    def run(self, *, created_at: str, proposal_text: str, executor: Callable[[Proposal], str] | None = None) -> NetworkLifecycleResult:
        return run_network_lifecycle_mvp(
            database=self.database,
            vault_path=self.vault_path,
            password=self.password,
            created_at=created_at,
            proposal_text=proposal_text,
            executor=executor,
            bootstrap=self.bootstrap,
            runtime=self.runtime,
        )

    def remove_agent(self, agent_id: str) -> None:
        self.runtime.remove_agent(agent_id)

    def snapshot(self, *, created_at: str) -> MembershipSnapshot:
        return self.runtime.snapshot(created_at=created_at)


__all__ = ["NetworkLifecycleResult", "NetworkLifecycleService", "run_network_lifecycle_mvp"]
