# F12 — Live Network Runtime

F12 converts the F11 identity/admission layer into a persistent live network.

## Contracts

- Membership registry: NetworkRuntime.add_agent() persists admitted agents; remove_agent() marks membership removed instead of deleting history.
- Handshake/session state: a completed F11 Handshake becomes an established persisted SessionState. Removing either endpoint closes its sessions.
- Peer discovery: discover_peers(agent_id) returns deterministic active peers excluding the requester.
- Membership snapshot: snapshot() freezes the active member IDs and persists an integrity-hashed snapshot.
- Snapshot quorum: for N active members, verification quorum is max(1, floor((N-1)/2)+1) because the proposer cannot verify itself.
- Snapshot-bound computation: run_snapshot_collective_computation() validates proposer/verifier membership against the explicit snapshot and passes that snapshot's quorum to the existing v2.7 collective runtime.

## Critical invariant

A live membership change after snapshot creation cannot change the quorum of an already-created computation:

live membership -> immutable snapshot S -> computation(S)

A later join/leave creates a new live state and, when requested, a new snapshot.

## Persistence

The initial F12 backend is SQLite. The domain contracts are independent of SQLite so the persistence implementation can later be moved to PostgreSQL/TimescaleDB without changing F11 identity or snapshot semantics.

## Runtime flow

Genesis -> Agent Identity -> Network Identity -> Membership -> Admission -> Handshake -> Live Registry -> Peer Discovery -> Membership Snapshot -> Snapshot Quorum -> Collective Computation -> Memory / Omega-Credit / Resource Allocation


## F12.5–F12.8 lifecycle

The live lifecycle is:

JOIN -> ADMISSION -> HANDSHAKE -> SESSION -> DISCOVERY -> SNAPSHOT -> COMPUTE -> LEAVE

heartbeat(session_id, seen_at=...) records the latest liveness observation for an established session. Historical session identity remains unchanged.

validate_snapshot_current(snapshot) is an explicit freshness guard for callers that require a computation to start only against the current membership epoch. It is intentionally separate from snapshot-bound computation: an already-created snapshot remains valid as historical evidence even after membership changes.

A reconnect reuses the immutable F11 identity and membership record. The runtime reactivates the member only with the same membership identity; it cannot replace it with a different membership record.

Removing an Agent deactivates its live membership and closes sessions involving that Agent. Historical membership and snapshots remain persisted.

This creates two deliberate semantics:

1. Historical reproducibility: old snapshots remain executable/auditable against their original quorum.
2. Fresh-start safety: a new computation can require validate_snapshot_current() before it begins.


## F12.9 hardening

Handshake registration is replay-protected at the persistent session layer: a handshake ID is unique, and attempting to register the same completed handshake again is rejected rather than replacing the existing session.

Membership transitions are append-audited through `network_runtime_membership_events`. Each join, leave, or rejoin advances the network membership epoch and records the affected Agent, event type, epoch, and creation marker.

The epoch therefore has an explicit audit interpretation:

`E0 -> JOIN(agent-0) -> E1 -> JOIN(agent-1) -> E2 -> ...`

The persisted audit event is evidence of the transition that produced the epoch. Historical snapshots continue to reference their own epoch and remain immutable.

The F11 cryptographic handshake contract remains the trust boundary for signatures; F12 session registration does not replace that verification. F12 adds persistence-level replay protection around an already-completed handshake.
