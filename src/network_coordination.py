"""F13 distributed coordination boundary for snapshot-scoped work."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from collections.abc import Iterable, Callable

from src.agent_state import AgentState
from src.collective_runtime import CollectiveComputationResult
from src.network_collective_runtime import run_snapshot_collective_computation
from src.network_runtime import MembershipSnapshot, NetworkRuntime
from src.proposal import Proposal
from src.resource_state import ResourceState
from src.verification import Verification


@dataclass(frozen=True)
class WorkAnnouncement:
    announcement_id: str
    network_id: str
    snapshot_id: str
    epoch: int
    proposer_id: str
    proposal_id: str
    status: str
    version: int = 1


@dataclass(frozen=True)
class CoordinationRecord:
    coordination_id: str
    network_id: str
    snapshot_id: str
    epoch: int
    proposal_id: str
    proposer_id: str
    verifier_ids: tuple[str, ...]
    quorum: int
    announcement_id: str
    version: int = 1


def _hash(payload: dict) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def create_work_announcement(
    snapshot: MembershipSnapshot,
    proposal: Proposal,
    *,
    status: str = "proposed",
) -> WorkAnnouncement:
    if proposal.proposer_id not in snapshot.members:
        raise ValueError("proposal proposer is not in membership snapshot")
    if not isinstance(status, str) or not status.strip():
        raise ValueError("status must be non-empty")
    payload = {
        "epoch": snapshot.epoch,
        "network_id": snapshot.network_id,
        "proposal_id": proposal.id,
        "proposer_id": proposal.proposer_id,
        "snapshot_id": snapshot.snapshot_id,
        "status": status,
        "version": 1,
    }
    return WorkAnnouncement(
        announcement_id=_hash(payload),
        network_id=snapshot.network_id,
        snapshot_id=snapshot.snapshot_id,
        epoch=snapshot.epoch,
        proposer_id=proposal.proposer_id,
        proposal_id=proposal.id,
        status=status,
    )


def verify_work_announcement(
    announcement: WorkAnnouncement,
    snapshot: MembershipSnapshot,
    proposal: Proposal,
) -> bool:
    expected = create_work_announcement(snapshot, proposal, status=announcement.status)
    return expected == announcement


def create_coordination_record(
    snapshot: MembershipSnapshot,
    proposal: Proposal,
    verifications: Iterable[Verification],
    *,
    announcement: WorkAnnouncement | None = None,
) -> CoordinationRecord:
    records = tuple(verifications)
    verifier_ids = tuple(record.verifier_id for record in records)
    if announcement is None:
        announcement = create_work_announcement(snapshot, proposal)
    if not verify_work_announcement(announcement, snapshot, proposal):
        raise ValueError("work announcement does not bind to snapshot and proposal")
    if len(verifier_ids) != len(set(verifier_ids)):
        raise ValueError("verifier ids must be unique")
    if proposal.proposer_id in verifier_ids:
        raise ValueError("proposer cannot verify its own proposal")
    if any(verifier_id not in snapshot.members for verifier_id in verifier_ids):
        raise ValueError("verifier is not in membership snapshot")
    if len(verifier_ids) < snapshot.quorum:
        raise ValueError("snapshot quorum has not been reached")
    payload = {
        "announcement_id": announcement.announcement_id,
        "epoch": snapshot.epoch,
        "network_id": snapshot.network_id,
        "proposal_id": proposal.id,
        "proposer_id": proposal.proposer_id,
        "quorum": snapshot.quorum,
        "snapshot_id": snapshot.snapshot_id,
        "verifier_ids": verifier_ids,
        "version": 1,
    }
    return CoordinationRecord(
        coordination_id=_hash(payload),
        network_id=snapshot.network_id,
        snapshot_id=snapshot.snapshot_id,
        epoch=snapshot.epoch,
        proposal_id=proposal.id,
        proposer_id=proposal.proposer_id,
        verifier_ids=verifier_ids,
        quorum=snapshot.quorum,
        announcement_id=announcement.announcement_id,
    )


def verify_coordination_record(
    record: CoordinationRecord,
    snapshot: MembershipSnapshot,
    proposal: Proposal,
) -> bool:
    if record.network_id != snapshot.network_id:
        return False
    if record.snapshot_id != snapshot.snapshot_id or record.epoch != snapshot.epoch:
        return False
    if record.proposal_id != proposal.id or record.proposer_id != proposal.proposer_id:
        return False
    announcement = create_work_announcement(snapshot, proposal)
    if record.announcement_id != announcement.announcement_id:
        return False
    expected = create_coordination_record(
        snapshot,
        proposal,
        tuple(
            Verification(
                id="",
                proposal_id=proposal.id,
                verifier_id=verifier_id,
                evidence="",
                valid=True,
                created_at=proposal.created_at,
            )
            for verifier_id in record.verifier_ids
        ),
        announcement=announcement,
    )
    return expected == record


def run_coordinated_snapshot_computation(
    runtime: NetworkRuntime,
    snapshot: MembershipSnapshot,
    current_state: AgentState,
    proposal: Proposal,
    verifications: Iterable[Verification],
    created_at: str,
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    executor: Callable[[Proposal], str],
    *,
    utility: float = 1.0,
    prior_commits: Iterable = (),
    require_current_snapshot: bool = True,
) -> tuple[CoordinationRecord, CollectiveComputationResult]:
    records = tuple(verifications)
    if require_current_snapshot:
        runtime.validate_snapshot_current(snapshot)
    runtime.validate_snapshot_verifiers(
        snapshot, proposal.proposer_id, (record.verifier_id for record in records)
    )
    coordination = create_coordination_record(snapshot, proposal, records)
    result = run_snapshot_collective_computation(
        runtime=runtime,
        snapshot=snapshot,
        current_state=current_state,
        proposal=proposal,
        verifications=records,
        created_at=created_at,
        memory_resource=memory_resource,
        compute_resource=compute_resource,
        executor=executor,
        utility=utility,
        prior_commits=prior_commits,
        require_current_snapshot=require_current_snapshot,
    )
    return coordination, result


__all__ = [
    "CoordinationRecord",
    "WorkAnnouncement",
    "create_coordination_record",
    "create_work_announcement",
    "run_coordinated_snapshot_computation",
    "verify_coordination_record",
    "verify_work_announcement",
]
