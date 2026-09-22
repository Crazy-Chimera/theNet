# Φ-Derived Allocation Extension

## Purpose

Provide a narrow adapter that derives Φ coherence directly from structural records before Ω-Credit allocation.

## Input

- relational utility records
- memory ResourceState
- compute ResourceState
- mapping from contributor ID to PhiStructure

## Output

The existing SelfOrganizingAllocation.

## Invariants

1. Every contributor with a utility record must have a PhiStructure.
2. Coherence is derived only through phi_coherence.
3. The adapter does not accept an independent coherence value.
4. Existing allocation rules remain unchanged.
5. Verified utility remains the only source of positive Ω-Credit.
6. Resource limits remain enforced by the existing allocator.
7. Inputs are not mutated.
8. No external service is required.

## Boundary

PhiStructure -> phi_coherence -> Ω-Credit -> memory/compute allocation.

The adapter composes existing primitives; it does not redefine Φ, Ω-Credit, or resource allocation.
