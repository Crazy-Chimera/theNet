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