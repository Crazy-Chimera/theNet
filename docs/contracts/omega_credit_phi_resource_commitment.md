# Ω-Credit Φ-Derived Resource Commitment Contract

## Purpose

Provide the end-to-end runtime boundary for:

`RelationalUtility + Φ structure + ResourceState -> Ω-Credit -> memory/compute state transition`.

The Φ structure is converted to a deterministic coherence value by the existing
`phi_coherence` primitive. The resulting coherence participates in Ω-Credit
allocation, which is then applied as an immutable local ResourceState transition.

This is an application-layer composition contract. It does not claim that the
software allocation is a physical energy or computation law.

## Input

- `utilities`: iterable of verified/unverified `RelationalUtility`.
- `memory_resource`: immutable `ResourceState`.
- `compute_resource`: immutable `ResourceState`.
- `structures_by_contributor`: contributor ID -> `PhiStructure`.
- `created_at`: non-empty timestamp for the resulting resource states.

## Process

1. Validate each utility and locate its Φ structure.
2. Derive Φ coherence for each contributor.
3. Compute self-organizing Ω-Credit allocation.
4. Convert allocation vectors into the immutable resource allocation.
5. Apply the allocation to memory and compute resources.

## Invariants

1. Missing Φ structure is rejected.
2. Unverified utility contributes zero Ω-Credit.
3. Φ coherence is deterministic for a fixed structure.
4. Resource capacity is never exceeded.
5. Zero allocation preserves the existing ResourceState object.
6. Inputs are not mutated.
7. The result is immutable.
8. No external service is required.
9. Same valid inputs produce the same resulting resource states.
10. The function composes existing primitives; it does not redefine Φ, Ω-Credit,
   ResourceState, or RelationalUtility semantics.
