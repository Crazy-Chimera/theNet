# Counterfactual Replay V1.2

Counterfactual Replay adds an isolated experimental branch to the deterministic Replay Engine.

## Contract

The baseline `RecursiveConvergenceRun` is immutable. A `CounterfactualSpec` identifies the exact cycle whose proposal input is replaced and the explicit counterfactual proposal.

The runner receives a new override mapping and produces a separate `RecursiveConvergenceRun`. The baseline is never modified.

## Evidence

The comparison reuses Replay V2 forensic comparison:

`BASELINE → selected input override → COUNTERFACTUAL → artifact comparison`

It reports baseline/counterfactual graph IDs, the selected cycle, both proposal texts, the first divergent artifact, and all cycle/artifact comparisons.

If the override is identical to the baseline input, the resulting run must remain deterministic. If it differs, divergence is expected at or after the selected input because downstream artifact IDs are content-derived.

## Control Room

The Control Room exposes a selected-cycle proposal override. This is an experimental branch, not a mutation of the canonical three-cycle experiment.

Counterfactual Replay demonstrates causal sensitivity of the implemented runtime artifact chain. It does not establish general intelligence, consciousness, or causality outside the modeled runtime.
