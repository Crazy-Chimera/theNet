# Counterfactual Impact Vector V1.5

V1.5 converts the V1.4 content diff into a structured observable difference vector.

For each cycle:

- ΔK
- ΔC
- ΔR
- ΔΦ
- Δutility
- ΔΩ-credit
- Δmemory available
- Δcompute available
- Δstate version
- changed field count

The aggregate is the arithmetic sum across cycles. It is intentionally **not**
a ranking, reward score, or causal inference. Zero means the compared numeric
observable did not change; non-zero means the two deterministic branches
produced different observable values.

The vector therefore supports branch-to-branch experiment comparison without
introducing an evaluative winner.
