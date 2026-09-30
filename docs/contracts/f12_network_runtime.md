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
