# Persistent Contribution Accounting Contract

## Purpose

Maintain an immutable, deterministic history of verified Ω-Credit records across multiple evolution events before distribution.

This layer answers:

`what verified contribution records have accumulated, and what is the aggregate credit per contributor?`

It does not create credit, verify proposals, decide consensus, or allocate resources.

## Input

A finite sequence of immutable `OmegaCredit` records.

## Output

An immutable `ContributionLedger` containing:

- `id`
- `entries`: canonical ordered credit record IDs
- `totals`: sorted `(contributor_id, total_credit)` tuples
- `version = 1`

## Invariants

1. Every entry must be an `OmegaCredit`.
2. Entry IDs must be unique; replaying the same record is rejected.
3. Multiple records may belong to the same contributor.
4. Only the credit already computed by `OmegaCredit` is accumulated.
5. Total contributor credit is the sum of that contributor's records.
6. Entries are canonically ordered by record ID.
7. Totals are canonically ordered by contributor ID.
8. Input records are not mutated.
9. The output is immutable.
10. Same record set produces the same ledger identity.
11. No external service is required.
12. The ledger does not infer truth, trust, consensus, or reputation.

## Architectural role

`verified relational utility + resource efficiency + Φ coherence → Ω-Credit`

`Ω-Credit records → persistent contribution ledger → aggregate contributor credit`

The aggregate can then be converted into a deterministic Ω-Credit distribution and consumed by resource allocation.
