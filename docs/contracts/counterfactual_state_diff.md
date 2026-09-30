# Counterfactual Replay V1.4 — State Diff

V1.4 compares observable runtime content, not merely content-derived artifact IDs.

For each cycle it compares:

- state fields;
- K/C/R/Φ convergence metrics;
- outcome result/success/utility;
- relational utility;
- Ω-Credit;
- memory resource state;
- compute resource state.

Numeric fields additionally expose:

`delta = counterfactual - baseline`

The baseline remains immutable.

## Interpretation

A changed proposal can therefore be inspected as:

`proposal → artifact divergence → state/content difference → metric/resource difference → next cycle`

The output is an operational diff of the implemented runtime. It is not an independent causal inference engine and does not establish physical causality, intelligence, consciousness, or agency.
