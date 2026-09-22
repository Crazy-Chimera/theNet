# Execution Chain Contract — Iteration 26

## Purpose

Validate continuity of an immutable execution sequence. The audit surface answers "what records exist"; this layer answers whether adjacent execution records form a continuous resource-state chain.

## Input

- Iterable of `ExecutionRecord` objects.

## Output

Immutable `ExecutionChain` containing:
- `id`
- `records`
- `continuous`
- `version = 1`

## Continuity rule

For every adjacent pair:
- previous `memory_after_id` must equal next `memory_before_id`
- previous `compute_after_id` must equal next `compute_before_id`

A single record is continuous by definition. An empty sequence is valid and continuous.

## Invariants

1. Only `ExecutionRecord` objects are accepted.
2. Input order is semantic and therefore preserved.
3. The same ordered record sequence produces the same chain identity.
4. Reordering records changes identity.
5. A broken memory or compute boundary makes `continuous = False`.
6. Output is immutable.
7. The chain does not infer correctness of the underlying execution, verification, consensus, or causal truth.
8. No external service is required.

## Boundary

ExecutionRecord provides immutable provenance for one resource transition. ExecutionChain provides a deterministic continuity check across an explicitly ordered sequence. It does not replace verification or consensus.
