# Deterministic Replay Contract

## Purpose

The Replay Engine executes the canonical Control Room experiment twice and compares the resulting immutable recursive computation.

## Comparison

The engine compares:

- complete `RecursiveConvergenceRun` equality
- canonical Evidence Graph equality
- ordered artifact IDs for each cycle
- cycle counts

A replay is deterministic only when all comparison dimensions match.

## Control Room endpoint

`POST /v1/control/replay` runs the canonical three-cycle experiment twice and returns:

- `deterministic`
- `graph_match`
- `run_match`
- `artifact_match`
- original and replay graph IDs
- original and replay cycle counts

## Safety

Replay is read-only with respect to the original run. It creates a fresh deterministic run and never mutates the original artifacts.

Replay does not establish intelligence, consciousness, truth, or correctness of the underlying theory. It establishes reproducibility of the implemented MVP computation.

## Forensic divergence report

Replay v2 also compares each cycle artifact in canonical order:

1. proposal
2. consensus
3. convergence
4. execution
5. commit
6. outcome
7. utility
8. Ω-Credit
9. memory
10. state

The response includes artifact_comparisons for every cycle and artifact. When a mismatch exists, the engine records the first divergence:

- first_divergence_cycle
- first_divergence_artifact
- first_divergence_original_id
- first_divergence_replay_id

The first divergence is diagnostic evidence only; it does not infer why the divergence occurred.

## Control Room presentation

The Control Room renders the forensic report beneath the deterministic status, allowing an operator to inspect every artifact pair and immediately locate the first differing artifact.
