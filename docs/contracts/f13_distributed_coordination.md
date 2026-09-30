# F13 — Distributed Network Coordination

F13 adds a coordination boundary above the F12 live network runtime.

## Purpose

F12 defines live membership and immutable membership snapshots. F13 binds distributed work to that snapshot so a proposal cannot silently change its participant set while coordination is in progress.

The coordination chain is:

`LIVE MEMBERSHIP → SNAPSHOT → WORK ANNOUNCEMENT → VERIFICATIONS → QUORUM → COORDINATION RECORD → COMPUTATION`

## Work announcement

`WorkAnnouncement` is an immutable, content-addressed description of proposed work:

- network ID
- snapshot ID
- membership epoch
- proposer
- proposal ID
- status

The announcement ID is derived from those fields. It therefore identifies the exact snapshot-scoped work item.

## Coordination record

`CoordinationRecord` freezes:

- network ID
- snapshot ID
- epoch
- proposal ID
- proposer
- verifier IDs
- snapshot-derived quorum
- announcement ID

Creation rejects:

- verifications for another proposal
- invalid verifications
- duplicate verifier IDs
- proposer self-verification
- verifiers outside the snapshot
- insufficient quorum

The record is deterministic and content-addressed.

## Execution boundary

`run_coordinated_snapshot_computation` performs:

1. optional fresh-snapshot validation;
2. snapshot verifier validation;
3. immutable coordination-record creation;
4. delegation to the existing F12 snapshot collective runtime.

The default is `require_current_snapshot=True`, so new distributed computations are safe against membership changes. Historical computations remain reproducible through the existing explicit snapshot API.

## Invariant

A later JOIN or LEAVE changes the live membership epoch but does not rewrite an existing snapshot or coordination record.

Therefore:

`coordination(snapshot_t) != coordination(snapshot_t+1)`

even when the proposal text is identical.

F13 is a coordination protocol boundary; it does not introduce a second consensus algorithm. Quorum remains derived from the F12 membership snapshot policy.
