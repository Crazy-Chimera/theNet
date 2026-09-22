# Self-Organizing Memory / Compute Allocation Contract

## Purpose

This layer composes three already-defined signals:

VERIFIED RELATIONAL UTILITY + RESOURCE STATE + Φ-DERIVED COHERENCE → Ω-CREDIT → RESOURCE ALLOCATION

It exposes separate memory and compute allocation pools without introducing a new trust or consensus mechanism.

## Input

- verified or unverified RelationalUtility records
- memory ResourceState
- compute ResourceState
- Φ-derived coherence per contributor, in [0, 1]
- allocation capacities are derived from each resource state's currently available capacity minus used capacity

## Output

Immutable AllocationResult containing:
- memory allocations
- compute allocations

Each allocation is produced by the existing Ω-Credit proportional allocator.

## Invariants

1. Only verified relational utility can generate positive Ω-Credit.
2. Utility, resource efficiency and Φ coherence are all multiplicative inputs to credit.
3. Invalid coherence values are rejected.
4. Memory and compute pools are allocated independently.
5. No pool can allocate more than its current remaining capacity.
6. Contributor ordering does not affect the result.
7. Existing utility and resource records are not mutated.
8. No external service is required.
9. This layer does not create consensus, infer reputation, modify agent state, or write memory.
10. Allocation is a resource consequence of verified signals, not a political or governance decision.

## Boundary

RelationalUtility supplies verified contribution evidence. ResourceState supplies local capacity. Φ supplies structural coherence. Ω-Credit combines them. This layer maps the resulting credit into separate memory and compute resource pools.
