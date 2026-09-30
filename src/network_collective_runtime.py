"""F12 adapter binding collective computation to an immutable network snapshot."""
from __future__ import annotations
from collections.abc import Callable, Iterable
from src.agent_state import AgentState
from src.collective_runtime import CollectiveComputationResult, run_collective_computation
from src.network_runtime import MembershipSnapshot, NetworkRuntime
from src.proposal import Proposal
from src.resource_state import ResourceState
from src.verification import Verification

def run_snapshot_collective_computation(
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
) -> CollectiveComputationResult:
    if not isinstance(runtime, NetworkRuntime):
        raise TypeError("runtime must be NetworkRuntime")
    if not isinstance(snapshot, MembershipSnapshot):
        raise TypeError("snapshot must be MembershipSnapshot")
    records = tuple(verifications)
    runtime.validate_snapshot_verifiers(
        snapshot, proposal.proposer_id, (record.verifier_id for record in records)
    )
    if current_state.subject_id != proposal.proposer_id:
        raise ValueError("proposal proposer must match current agent state")
    return run_collective_computation(
        current_state, proposal, records, snapshot.quorum,
        f"iota:collective:{snapshot.snapshot_id}:{proposal.id}",
        created_at, memory_resource, compute_resource, executor,
        utility=utility, prior_commits=prior_commits,
    )

__all__=["run_snapshot_collective_computation"]
