# F10.1 — Recursive Learning Metrics

F10.1 extends F10 from recursive convergence to an operational test for
measurable learning across cycles.

It does not claim intelligence, consciousness, AGI, or semantic understanding.

## Learning condition

A cycle is marked verified_improvement=true only when:

1. its proposal explicitly depends on the previous cycle's memory;
2. no tracked performance dimension regresses; and
3. at least one tracked performance dimension strictly improves.

Tracked dimensions:

- outcome utility — higher is better;
- Omega-Credit — higher verified contribution is better;
- resource efficiency — higher is better;
- K — invariant consistency;
- C — structural complexity proxy, lower is better;
- Phi — structural coherence, higher is better.

R is reported but not treated as a learning improvement dimension because the
current runtime's recursive artifact chain is structurally fixed.

## Per-cycle observables

Each cycle exposes:

- proposal novelty — deterministic lexical novelty proxy against the previous proposal;
- utility;
- Omega-Credit;
- resource efficiency;
- K / C / R / Phi;
- state version delta;
- explicit memory dependency;
- verified improvement flag.

Proposal novelty is intentionally described as a lexical proxy, not semantic
novelty.

## Recursive runtime

run_recursive_convergence(...) now accepts an optional utility_builder so
deterministic simulations can vary measured outcome utility between cycles.
The default behavior remains unchanged.

The run exposes:

run.learning_metrics

which returns one immutable RecursiveLearningMetrics record per cycle.

## Interpretation

The distinction is:

repetition
-> another cycle executes

recursive dependency
-> the next proposal references verified prior memory

measurable improvement
-> verified prior memory is used and at least one measured performance
dimension improves without regression

Only the third condition is counted as operational recursive learning.

## Non-goals

F10.1 does not establish:

- general intelligence;
- autonomous goal generation;
- semantic understanding;
- consciousness;
- self-modifying code;
- AGI.

It establishes a deterministic measurement contract for a narrower claim:
a recursive agent can be tested for verified improvement across successive
collective-computation cycles.
