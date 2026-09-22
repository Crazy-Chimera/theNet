# Φ Structure Contract

## Purpose

Φ is the canonical structural layer of theNet. It derives an immutable relational topology from explicit Relation objects. It represents relational form only; it does not assign meaning or establish verification, consensus, contribution, memory, convergence, or safety.

## Input

An iterable of Relation objects.

Duplicate relations are allowed and are deduplicated structurally. Input order is not semantically significant. An empty iterable is valid.

## Output

An immutable PhiStructure containing:

- id
- relation_ids: sorted unique relation identifiers
- node_ids: sorted unique source and target identifiers
- edges: sorted unique directed source/target pairs
- version = 1

## Identity

The structure ID is SHA-256 over the canonical topology fields and version. Equivalent relation collections therefore produce the same structural identity.

## Invariants

1. Every input item must be a Relation.
2. Duplicate relations do not change the resulting topology.
3. Relation order does not change the resulting topology.
4. Node identifiers are derived only from relation endpoints.
5. Directed edge orientation is preserved.
6. Empty input is valid and deterministic.
7. The returned structure is immutable.
8. Input collections and Relation objects are not mutated.
9. No external service is required.
10. Φ describes structure only; it does not establish verification, consensus, contribution, memory, convergence, meaning, or safety.

## Architectural boundary

Genesis creates subjects. Relation creates directed links. Φ composes those links into canonical topology. Φ-derived coherence and later layers consume this topology without redefining its structural identity.
