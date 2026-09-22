# Ledger-Backed Ω-Credit Resource Commitment Contract

## Purpose

Bind persistent contribution accounting to the canonical Ω-Credit resource transition.

The commitment path is:

`ContributionLedger → Ω-Credit Distribution → Ω-Credit Allocation → ResourceState transition`

## Input

- immutable `ContributionLedger`
- finite memory capacity
- finite compute capacity
- current immutable memory `ResourceState`
- current immutable compute `ResourceState`
- non-empty creation timestamp

## Output

A pair of new immutable `ResourceState` values.

## Invariants

1. The ledger is the only contribution source for this path.
2. Distribution is derived deterministically from the complete ledger totals.
3. Allocation is derived only from that distribution and supplied capacities.
4. Memory and compute transitions use the canonical Ω-Credit commitment layer.
5. Existing resource state is not mutated.
6. Allocation cannot exceed remaining capacity.
7. Empty/zero-credit ledgers produce no resource transition.
8. Same ledger and capacities produce the same allocation before timestamped resource transition.
9. No consensus or verification is performed in this layer; those are upstream.
10. No external service is required.

## Architectural role

`verified evolution → Ω-Credit records → persistent ledger → canonical distribution → resource allocation → ResourceState`

This closes the accounting-to-resource boundary without coupling contribution measurement to resource mutation.
