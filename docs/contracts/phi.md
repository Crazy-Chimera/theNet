# Φ Structure Contract

Φ is the structural layer: the network form created by relations. In theNet, this iteration implements a bounded graph-structural proxy for Φ; it is not a claim that software computes physical quantum entanglement.

## Input
- node_ids: non-empty sequence of unique non-empty strings.
- relation_ids: sequence of unique non-empty strings.

## Output
Immutable PhiStructure with deterministic id, sorted node_ids, sorted relation_ids, density in [0,1], version 1.

For N distinct nodes: density = relation_count / (N * (N - 1)). The value is capped at 1.0; self-relations are not part of the denominator.

## Invariants
1. Node identifiers are non-empty and unique.
2. Relation identifiers are non-empty and unique.
3. Snapshot is immutable.
4. Equivalent inputs produce the same canonical ordering, density, and ID.
5. Changing a node or relation changes structural identity.
6. A single node has density 0.0.
7. Empty relation set is valid for a non-empty node set.
8. No external service is required.
9. Φ does not imply process, memory, verification, consensus, contribution, meaning, or convergence.

## Boundary
Genesis creates nodes. Relation creates directed links. Φ observes the resulting relational structure. Later layers may use Φ as one input to coherence/resonance or convergence.
