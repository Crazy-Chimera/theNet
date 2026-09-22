# Ω-Credit Resource Allocation Contract

## Purpose

Convert an already verified Ω-Credit distribution into a deterministic resource allocation.

This layer answers only:

`how should available resources be divided according to the supplied verified contribution shares?`

It does not create Ω-Credit, verify contributions, infer trust, establish consensus, or mutate the resource state.

## Input

- an `OmegaCreditDistribution`
- a finite non-negative memory capacity
- a finite non-negative compute capacity

The distribution already contains normalized contribution shares.

## Output

An immutable `OmegaCreditAllocation` containing:

- `id`
- `memory_by_contributor`
- `compute_by_contributor`
- `version = 1`

Only contributors present in the distribution receive an allocation.

## Allocation rule

For contributor `i` with distribution share `s_i`:

`memory_i = memory_capacity × s_i`

`compute_i = compute_capacity × s_i`

When the distribution has zero total credit, every allocation is zero.

## Invariants

1. The distribution must be an `OmegaCreditDistribution`.
2. Capacities must be finite and non-negative.
3. Every allocation is non-negative.
4. Allocation is proportional only to the supplied contribution share.
5. The sum of allocations equals the supplied capacity within floating-point tolerance.
6. Input distribution is not mutated.
7. The output is immutable.
8. Input order cannot affect the allocation.
9. No external service is required.
10. This layer does not establish truth, verification, consensus, reputation, or meaning.
11. Resource mutation remains outside this pure allocation layer.

## Architectural role

`verified relational utility + Resource State + Φ coherence → Ω-Credit`

`Ω-Credit → distributed contribution shares → resource allocation`

The allocator therefore keeps contribution measurement, contribution aggregation, and resource transfer as separate verifiable boundaries.
