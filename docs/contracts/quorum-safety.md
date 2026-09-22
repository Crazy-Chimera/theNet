# Quorum Safety and Genesis Evolution

## Purpose

This contract separates **protocol quorum** from **majority consensus**.

The Genesis simulation intentionally allows an explicit quorum lower than the population size. Therefore a higher recursive-depth/reputation value (R) is not a prerequisite for proposal-driven evolution in the current protocol.

## Properties

- `quorum = 1` with two agents permits evolution after one independent verifier.
- `quorum = 2` with three agents permits evolution after two independent verifiers.
- `quorum > available_verifiers` blocks evolution.
- A quorum value alone does not imply majority consensus.
- Majority consensus requires an explicit threshold derived from the eligible verifier population; it must not be inferred from `quorum`.
- The proposer cannot verify its own proposal.
- One verifier cannot create majority consensus over a population that contains more than two eligible participants unless the protocol explicitly defines a different voting rule.

## Security boundary

Removing higher R does not remove the need for identity and Sybil resistance. If creating additional verifier identities is costless, an attacker may increase the apparent verifier count without increasing independent evidence.

Therefore:

`quorum != independence`

and:

`verifier_count != epistemic_strength`

The current Genesis simulation proves only that **explicit quorum-gated evolution is mechanically possible without a higher R requirement**. It does not prove that the resulting decision is resistant to Sybil attacks or that the quorum is socially or epistemically sufficient.

## Design consequence

theNet should keep three concerns separate:

1. **Eligibility** — who may verify.
2. **Quorum** — how many eligible verifiers are required.
3. **Independence / weight** — why those verifiers represent distinct evidence.

R may later be used as one eligibility or weighting signal, but the protocol must not make R an implicit prerequisite for basic proposal simulation.