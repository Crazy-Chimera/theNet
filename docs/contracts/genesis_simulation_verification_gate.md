# Genesis Simulation → Verification Gate Integration Contract

## Purpose

Make the Genesis proposal simulation consume the explicit bootstrap verification gate instead of duplicating its population/quorum feasibility rule.

## Rule

For a simulation with population size P and quorum Q, the simulation requests Q independent verifiers. The bootstrap gate is evaluated with:

- population_size = P
- verifier_count = Q
- required_quorum = Q

The simulation may proceed only when the gate is approved.

## Invariants

1. The proposer is never counted as a verifier.
2. A quorum Q requires at least Q independent agents in addition to the proposer.
3. The simulation and the bootstrap gate must agree on feasibility.
4. The integration does not introduce reputation requirements.
5. Existing deterministic proposal, verification, consensus, and evolution identities remain unchanged.
6. No new external dependency is introduced.

## Verification

Existing Genesis simulation behavior remains valid. Tests additionally establish that the reachable-quorum boundary is enforced through the bootstrap verification primitive.