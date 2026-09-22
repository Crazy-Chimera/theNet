# Collective Consensus Contract

## Purpose

Add an explicit collective-consensus layer without redefining Gamma convergence.

Gamma answers whether proposal identifiers converge to one resolved proposal.
Consensus answers whether enough independent verifiers support that proposal.

## Input

- proposal_id: non-empty string
- verifications: non-empty collection of Verification records
- quorum: positive integer

## Output

Immutable Consensus:

- id
- proposal_id
- verification_ids
- verifier_ids
- quorum
- reached
- version = 1

## Invariants

1. All verification records refer to the same proposal.
2. Every verification must be valid.
3. Each verifier may count at most once.
4. reached is true only when distinct valid verifiers >= quorum.
5. The same canonical input produces the same ID.
6. Consensus does not mutate proposals, verifications, or agent state.
7. Consensus is distinct from Gamma convergence.
8. A single verifier may satisfy quorum=1; higher quorum is an explicit policy choice, not an implicit requirement of convergence.

## Boundary

- Gamma convergence establishes proposal identity agreement.
- Consensus establishes sufficient independent verification under a declared quorum.
- Evolution commit may later require Consensus when the runtime policy demands collective verification.
