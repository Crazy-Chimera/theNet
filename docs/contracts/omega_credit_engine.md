# Ω-Credit Distributed Contribution Contract

## Purpose

Aggregate independently produced Ω-Credit records into a deterministic contribution distribution.

This layer answers only:

`who contributed how much verified relational utility under the supplied state?`

It does not create credit, verify proposals, mutate resources, or decide consensus.

## Input

A finite iterable of immutable `OmegaCredit` records.

## Output

An immutable `OmegaCreditDistribution` containing:

- `id`
- `total_credit`
- `contributions`: sorted `(contributor_id, credit, share)` tuples
- `version = 1`

## Distribution rule

For total credit:

`total = Σ credit_i`

For each contributor:

`share_i = credit_i / total`

When `total = 0`, every share is `0`.

Contributions are sorted by contributor identifier so input order does not affect the result.

## Invariants

1. Every input item must be an `OmegaCredit`.
2. Each contributor may appear at most once in the aggregation.
3. Credit values are already bounded by the Ω-Credit primitive.
4. Shares are bounded to [0, 1].
5. Non-zero total credit produces shares summing to 1 within floating-point tolerance.
6. Zero total credit produces zero shares.
7. Input records are not mutated.
8. The output is immutable.
9. Same credit set produces the same distribution identity.
10. This layer does not infer trust, truth, consensus, or reputation.
11. No external service is required.

## Architectural role

`verified relational utility + Resource State + Φ coherence → Ω-Credit`

`Ω-Credit records → distributed contribution aggregation → contribution shares`

The resulting distribution can be consumed by a later allocation layer without coupling contribution measurement to resource transfer.
