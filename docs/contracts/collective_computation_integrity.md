# Iteration 28 — Collective Computation Integrity Contract

## Purpose

Provide a pure audit boundary for a completed Collective Computation Cycle. The integrity check validates that the cycle's internal references still satisfy the collective-computation contract before the result is accepted by a caller.

This is an audit primitive, not a second consensus mechanism.

## Input

- one immutable `CollectiveComputationCycle`.

## Output

- `True` when all cross-layer references are internally consistent;
- `False` otherwise.

## Checks

1. Collective consensus is reached.
2. The evolution commit references the consensus verification IDs.
3. The committed memory references the evolution commit.
4. The relational utility is verified and references the committed memory.
5. Every verifier Relation corresponds to a consensus verifier.
6. Φ contains exactly the cycle's verifier Relation IDs.
7. Φ edges preserve the Relation source-to-verifier direction.
8. Resource states remain immutable `ResourceState` values.

## Invariants

- The audit does not mutate the cycle.
- The audit performs no external I/O.
- A structurally invalid cycle is rejected rather than repaired.
- The audit does not infer truth beyond the explicit cycle records.
- A valid result is deterministic for the same immutable cycle.

## Boundary

`collective_computation.py` constructs the cycle. This module only audits the cross-layer consistency of that completed result.
