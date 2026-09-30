# Ω Control Room

The Control Room is the first observable UI surface for the recursive Agent Ω runtime.

## Purpose

The UI exposes runtime evidence rather than inventing a parallel decision layer. The first vertical slice makes the F10 → F10.1 → F10.2 → F10.3 loop inspectable:

```
proposal
  ↓
verification
  ↓
consensus
  ↓
convergence
  ↓
outcome
  ↓
Ω-Credit
  ↓
verified learning
  ↓
adaptive allocation
  ↓
next cycle
```

## Runtime boundary

The browser calls `POST /v1/control/demo`. The endpoint executes the existing recursive convergence runtime with:

- 3 Genesis agents
- quorum 2
- 3 recursive cycles
- deterministic executor
- F10.3 memory/compute capacities of 100
- utility builder producing 0.5, 1.0, 1.0

The endpoint returns a deliberately compact read model containing proposal IDs, parent memory dependencies, outcomes, Ω-Credit, K/C/R/Φ, learning flags, and adaptive allocation.

This is a deterministic demonstration endpoint, not a production workload executor.

## UI invariants

- The frontend does not calculate consensus, Ω-Credit, convergence, or verified improvement.
- K/C/R/Φ are displayed as project-level operational metrics.
- "VERIFIED IMPROVEMENT" is shown only when the runtime returns `verified_improvement=true`.
- Resource allocation is displayed from the immutable allocation returned by the runtime.
- IDs are shown for auditability and traceability.

## Next slices

1. Replace the demo endpoint with persisted live recursive runs.
2. Add a cycle detail view for Proposal → Verification → Consensus → Outcome → Memory.
3. Add immutable execution-audit browsing.
4. Add Agent and relation graph views.
5. Add Genesis/bootstrap controls.
6. Add streaming events only after the underlying runtime state is durable and queryable.

The Control Room does not establish AGI, consciousness, or general intelligence. It makes the implemented computational contracts observable.
