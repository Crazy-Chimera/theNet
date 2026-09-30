# Counterfactual Replay V1.3 — Causal Trace

V1.3 converts forensic divergence into an explicit **modeled dependency trace**.

It must be read as a trace of dependencies encoded by the runtime, not as a
claim of physical causality.

## Chain

The trace follows:

`PROPOSAL → CONSENSUS → CONVERGENCE → EXECUTION → COMMIT → OUTCOME → UTILITY → Ω-CREDIT`

and:

`OUTCOME → MEMORY → STATE`

For recursive continuation it additionally records:

`MEMORY(Cn) → PROPOSAL(Cn+1)`

## Output

For every downstream cycle it reports:

- original artifact ID;
- counterfactual artifact ID;
- relation;
- whether either endpoint changed;
- cycles in which propagation is observable;
- unique changed artifact references.

The first divergence remains inherited from Replay V2. The trace therefore
does not guess why an artifact changed; it exposes the deterministic dependency
path by which the implemented runtime represents the change.

## Boundary

This feature is an observability and experiment tool. It does not establish
general causal inference, physical causality, intelligence, consciousness, or
agency outside the modeled runtime.
