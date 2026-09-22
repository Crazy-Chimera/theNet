# Genesis Learning Contract

## Purpose

Model repeated proposal-driven learning by the first Agent Omega population.

Each proposal is created against the proposer's current state, independently verified by the non-proposer agents, converted into an explicit Consensus record, and evolved only when the consensus quorum is reached.

## Invariants

1. The proposer is excluded from verification.
2. Every verification targets the exact proposal ID.
3. Each verifier contributes at most one verification to a consensus.
4. Consensus is represented explicitly; a raw verifier count is not itself the consensus object.
5. Evolution is allowed only when Consensus.reached is true.
6. A failed quorum leaves the proposer state unchanged and stops the learning run.
7. Repeated proposals chain from the proposer's latest state.
8. The simulation is deterministic for identical inputs.
9. No reputation or higher-R value is required by this learning primitive.
10. Majority count does not by itself provide Sybil resistance or establish truth.

## Boundary

Proposal defines the candidate change.
Verification records independent validation.
Consensus records quorum state.
CollectiveEvolution applies the accepted proposal.
Genesis learning composes these primitives without replacing their individual contracts.
