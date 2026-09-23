# Iteration 39 — Replay-Safe Collective Evolution Contract

## Purpose

Collective evolution must not apply the same proposal to the same prior state more than once. Consensus and evidence integrity establish that a proposal may be accepted; replay protection establishes that an accepted transition is applied at most once to a given state lineage.

This is a protocol integrity constraint, not a consensus rule.

## Guard input

- candidate `EvolutionCommit`
- iterable of previously committed `EvolutionCommit` records

## Rules

Reject when:

1. candidate is not an `EvolutionCommit`;
2. any history item is not an `EvolutionCommit`;
3. candidate commit ID already exists in history;
4. the same `proposal_id` was already committed from the same `previous_state_id`.

Allow when:

- the proposal is the same but targets a different previous state;
- the previous state is the same but the proposal is different.

The guard is deterministic, immutable, and has no external dependency.

## Integration

`evolve_collectively(..., prior_commits=())` invokes the guard before mutating the Agent Ω state. Existing callers remain valid because the history defaults to empty.

Replay protection does not replace consensus, verification, convergence, or evidence-integrity checks. It is an additional transition-safety boundary.
