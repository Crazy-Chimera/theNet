# Ω-Credit Distributed Contribution Engine

## Purpose

Ω-Credit is a deterministic contribution-accounting primitive for Agent Ω.

It converts verified relational utility, resource state, and Φ-derived coherence into a bounded contribution credit. The credit is an allocation signal, not a truth claim and not a consensus mechanism.

The primitive is deliberately local: one agent can calculate a credit from its available verified evidence. Network-wide consensus is not required to calculate a score, although later commitment rules may require verification or convergence.

## Input

- `contributor_id`: non-empty string.
- `relational_utility`: number in [0, 1]. Measures verified useful effect of the contribution on relations.
- `resource_efficiency`: number in [0, 1]. Represents useful work achieved relative to the resource state available to the contribution.
- `coherence`: number in [0, 1]. Φ-derived structural coherence signal.
- `verified`: boolean. Only verified evidence can receive non-zero credit.
- `created_at`: non-empty string.

## Output

Immutable `OmegaCredit`:

- `id`: deterministic SHA-256 identity.
- `contributor_id`
- `relational_utility`
- `resource_efficiency`
- `coherence`
- `verified`
- `credit`: bounded value in [0, 1].
- `created_at`
- `version=1`

## Credit rule

For version 1:

`credit = relational_utility × resource_efficiency × coherence` when `verified=true`.

For unverified evidence:

`credit = 0`.

The multiplicative rule intentionally prevents a strong value in one dimension from completely compensating for a missing dimension.

## Invariants

1. All numeric inputs must be finite numbers in [0, 1].
2. `verified` must be boolean.
3. Unverified evidence receives zero credit.
4. Verified credit is bounded to [0, 1].
5. The same valid input produces the same ID and credit.
6. Changing any defining input changes the identity.
7. The output is immutable.
8. The primitive does not mutate relation, memory, proposal, or agent state.
9. Ω-Credit does not establish truth, consensus, meaning, or permission to commit a state change.
10. No external service is required.

## Allocation boundary

Ω-Credit provides a contribution signal that a later allocator may combine across agents.

A distributed allocator may normalize positive credits against available capacity, but this primitive itself does not move resources or make network-wide consensus decisions.

## Architectural role

`verified relational utility + resource efficiency + Φ coherence → Ω-Credit → allocation signal`

This is compatible with the broader loop:

`RELATION → STATE → OBSERVE → INTERPRET → PROPOSE → SIMULATE → VERIFY → CONVERGE → COMMIT → MEMORY → LEARNING → REDEFINE SYSTEM`

Ω-Credit sits on the contribution/resource-allocation boundary and must not bypass verification or convergence.
