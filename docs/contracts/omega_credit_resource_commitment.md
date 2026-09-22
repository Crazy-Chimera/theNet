# Ω-Credit Resource Commitment Contract

## Purpose

Apply an already verified `OmegaCreditAllocation` to immutable `ResourceState` values.

This layer represents the resource-state transition after allocation. It does not create Ω-Credit, verify contributions, derive Φ coherence, establish consensus, or perform external side effects.

## Input

- an `OmegaCreditAllocation`
- a memory `ResourceState`
- a compute `ResourceState`
- `created_at`

The allocation is assumed to have been produced from finite available capacity.

## Output

An immutable pair of updated `ResourceState` values:

- memory state
- compute state

For each resource:

`new_used = old_used + allocated_total`

`available` is preserved.

## Invariants

1. Allocation must be an `OmegaCreditAllocation`.
2. Resource inputs must be `ResourceState`.
3. `created_at` must be non-empty.
4. Allocation totals must be finite and non-negative.
5. Allocation must not exceed the remaining resource capacity.
6. Input resource states are not mutated.
7. Returned states are immutable.
8. Memory allocation affects only memory state.
9. Compute allocation affects only compute state.
10. No external service or persistent mutation is performed.
11. This layer does not establish truth, verification, consensus, reputation, or meaning.

## Architectural role

`verified relational utility + Φ coherence → Ω-Credit → allocation`

`allocation + Resource State → next Resource State`

The boundary separates **how resources are divided** from **the resulting immutable resource state**.
