# Φ Structure Contract

## Purpose

Φ is the structural layer after Relation. It derives a deterministic structural fingerprint from explicit relations without changing those relations or asserting semantic truth.

## Input

- relations: an iterable of Relation objects.
- Relation fields used: id, source_id, target_id.

## Output

An immutable PhiStructure containing:

- id
- relation_ids
- node_ids
- edges: ordered (source_id, target_id) pairs
- version = 1
- edge_count and node_count derived from the immutable structure

## Identity

The structure ID is SHA-256 over canonical relation IDs, node IDs, edges, and version. Duplicate input occurrences of the same relation ID are collapsed into one structural edge. Input order does not affect the resulting identity.

## Invariants

1. Empty relation collections are valid.
2. Inputs must contain only Relation objects.
3. Duplicate relation IDs are deduplicated deterministically.
4. Input order does not affect identity.
5. Output is immutable.
6. Source Relation objects are not mutated.
7. Node IDs are derived from relation endpoints and returned in sorted order.
8. Edges are ordered by the sorted unique relation IDs.
9. edge_count equals the number of structural edges.
10. node_count equals the number of structural nodes.
11. Φ does not claim verification, consensus, contribution, meaning, memory, convergence, or truth.
12. No external services are required.

## Boundary

Relation defines explicit links. Φ describes their structural arrangement. Later layers may evaluate resonance, convergence, meaning, or verification.
