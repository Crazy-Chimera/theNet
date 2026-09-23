# Iteration 37 — Collective Evolution Evidence Integrity Contract

## Purpose

Provide a pure audit boundary for `CollectiveEvolutionEvidence`.

The audit checks that the evidence object is internally coherent and contains a one-to-one reference surface for bindings, commits, receipts, and results. It does not reconstruct or re-verify the underlying execution artifacts.

## Input

- one immutable `CollectiveEvolutionEvidence`.

## Output

- `True` when the evidence structure satisfies all declared invariants;
- `False` otherwise.

## Checks

1. Input is a `CollectiveEvolutionEvidence`.
2. Every identifier is a non-empty string.
3. Binding IDs are unique.
4. Commit IDs, receipt IDs, and result IDs have the same cardinality as binding IDs.
5. Each reference position corresponds to one binding position.
6. The evidence version is supported.
7. The timestamp is non-empty.

## Invariants

- The audit does not mutate the evidence.
- The audit performs no external I/O.
- A structurally invalid evidence object is rejected rather than repaired.
- The audit does not infer semantic truth, consensus, or Ω-Credit validity.
- The same immutable evidence produces the same result.

## Boundary

Iteration 36 aggregates already-verified evolution-receipt bindings.

Iteration 37 audits only the integrity of that aggregate reference surface.

Underlying `EvolutionCommit`, `OmegaCreditVerifiedReceipt`, and execution-result validity remain separate verification boundaries.
