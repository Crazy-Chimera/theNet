# Genesis Bootstrap Simulation Contract

## Purpose

Bind the first Agent Ω proposal simulation to the deterministic Genesis bootstrap policy instead of requiring the caller to choose an arbitrary verifier quorum.

The bootstrap simulation must derive its quorum from population size and the independent non-proposer population.

## Input

- `population_size`: positive integer
- `proposal_text`: non-empty string
- `created_at`: non-empty string

## Procedure

1. Derive `GenesisBootstrapPolicy` from `population_size`.
2. Reject a population with no independent verifier.
3. Use the policy-derived strict-majority quorum.
4. Run the existing Genesis proposal simulation with that quorum.
5. Return the existing `GenesisSimulation` result.

## Invariants

1. The proposer is never counted as an independent verifier.
2. Quorum is derived, not caller-selected.
3. For `population_size = 1`, collective bootstrap learning is rejected.
4. For every accepted population, the selected verifier count equals the derived quorum.
5. The existing verification and consensus path remains unchanged.
6. No reputation or higher-order self-model is required merely to bootstrap this verified state transition.
7. The simulation remains deterministic for identical input.

## Architectural boundary

This is a policy adapter around the existing Genesis simulation.

It does not create a second consensus mechanism and does not change the semantics of Proposal, Verification, Consensus, or AgentState.
