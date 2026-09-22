# Φ Structure — Contract

## Purpose

Φ is the structural layer of theNet. It derives an immutable relational topology from explicit Relation objects. The canonical Φ state contains the relation set, participating node set, and directed edges.

## Input

- An iterable of Relation objects.
- Duplicate relation objects are allowed and are deduplicated structurally.
- Input order is not semantically significant.
- An empty iterable is valid.

## Output

An immutable PhiStructure containing:

- id: SHA-256 identifier of the canonical topology.
- relation_ids: sorted unique relation identifiers.
- node_ids: sorted unique source and target identifiers.
- edges: sorted unique source/target pairs.
- version: 1.

## Identity

The identifier is derived from the canonical JSON representation of the topology fields and version, with sorted object keys and compact separators. Equivalent relation collections therefore produce the same structural identity.

## Invariants

1. Every input item must be a Relation.
2. Duplicate relations do not change the resulting topology.
3. Relation order does not change the resulting topology.
4. Node identifiers are derived only from relation endpoints.
5. Directed edge orientation is preserved.
6. The returned structure is immutable.
7. Empty input is valid and deterministic.
8. The input collection and relation objects are not mutated.
9. No external service is required.
10. Φ describes relational structure only; it does not by itself establish verification, consensus, contribution, memory, convergence, meaning, or safety.

## Boundary

- Genesis creates subjects.
- Relation creates directed links.
- Φ composes relations into canonical topology.
- Φ-derived coherence and later layers consume this topology without redefining its structural identity.
