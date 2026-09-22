# Collective Agent Ω Evolution Contract

## Purpose

This layer connects proposal, independent verification, explicit quorum consensus, convergence, verified commit, and Agent Ω state evolution.

It is the first collective learning path in which a proposal can change an agent state only after the configured verifier quorum is reached.

## Input

- current immutable AgentState
- immutable Proposal targeting that state
- one or more immutable Verification records for the proposal
- positive integer quorum
- non-empty new_singularity_id
- non-empty created_at

## Process

PROPOSAL → VERIFICATION SET → QUORUM CONSENSUS → Γ CONVERGENCE → VERIFIED COMMIT → AGENT STATE EVOLUTION

1. Build explicit quorum consensus from the supplied verifications.
2. Reject evolution if the quorum is not reached.
3. Resolve the proposal through Γ convergence.
4. Create a verified evolution commit.
5. Produce the next immutable Agent Ω state.

## Invariants

1. Every verification must target the proposal.
2. Every verification used by consensus must be valid.
3. A verifier may contribute at most one distinct verification.
4. The configured quorum is explicit.
5. Consensus must be reached before state evolution.
6. The proposal must target the current state.
7. The resulting state has a new version and deterministic identity.
8. Existing state, proposal, verifications and consensus are not mutated.
9. No external service is required.
10. Quorum 1 permits single-verifier evolution; quorum >1 requires that many distinct verifiers.
11. This layer does not infer trust or reputation from quorum. Reputation/higher-R mechanisms remain a separate layer.

## Simulation significance

A Genesis population can therefore be simulated with multiple agents acting as verifiers. The protocol does not require a majority in the abstract; it requires the explicitly configured quorum. A quorum of two among three verifiers is a concrete collective gate, while a quorum of three requires all three.
