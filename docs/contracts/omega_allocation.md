# Ω-Credit Allocation Contract

## Purpose

The allocation layer converts a set of Ω-Credit contribution signals into a deterministic proportional allocation plan.

It is the first distributed step above the individual Ω-Credit primitive. It does not transfer resources, establish consensus, or authorize a state commit.

## Input

- `credits`: iterable of `OmegaCredit` values.
- `capacity`: finite non-negative number representing the resource capacity available for this allocation cycle.

## Rule

1. Ignore credits whose `verified` flag is false or whose `credit` is zero.
2. Aggregate positive credit by `contributor_id`.
3. If total positive credit is greater than zero, allocate:

`allocation(contributor) = capacity × contributor_credit / total_credit`

4. If no positive credit exists, every allocation is zero.

## Output

Immutable `CreditAllocation` entries:

- `contributor_id`
- `credit`
- `allocation`
- `version=1`

The output sequence is sorted by contributor identifier.

## Invariants

1. Capacity must be finite and non-negative.
2. Invalid credit objects are rejected.
3. Allocation is deterministic.
4. Duplicate credit objects do not create duplicate contributor entries; their positive credit is aggregated.
5. Total allocation equals capacity when total positive credit exists, within floating-point tolerance.
6. Total allocation is zero when no positive credit exists.
7. No external service is required.
8. The allocator does not mutate credit objects.
9. Allocation is a planning signal, not an actual resource transfer.
10. Allocation does not establish truth, consensus, or permission to commit state.

## Architectural role

`verified relational utility + resource efficiency + Φ coherence → Ω-Credit → distributed allocation signal`

This permits resource allocation to emerge from verified contribution without making network-wide majority consensus a prerequisite for every local allocation calculation.
