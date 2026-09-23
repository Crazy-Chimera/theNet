# Φ Structure Contract

## Purpose

Φ is the structural layer after Relation. It derives a deterministic structural fingerprint from a finite set of relations without changing those relations or asserting semantic truth.

## Input

- relations: a finite collection of immutable Relation-like records.
- Each relation must expose id, source_id, target_id, and kind.

## Output

An immutable Structure containing:
- id
- relation_ids
- node_ids
- edge_count
- node_count
- version = 1

## Identity

The structure ID is SHA-256 over a canonical representation of the sorted relation IDs and version. The same relation set therefore produces the same structure identity independent of input order.

## Invariants

1. Empty relation collections are valid and produce an empty structure.
2. Every relation ID is a non-empty string.
3. Duplicate relation IDs are rejected; a structural snapshot must not silently collapse duplicate evidence.
4. Input order does not affect identity.
5. Output is immutable.
6. The source relation objects are not mutated.
7. Node IDs are derived from relation endpoints and returned in sorted order.
8. edge_count equals the number of relation IDs.
9. node_count equals the number of node IDs.
10. Φ does not claim verification, consensus, contribution, meaning, memory, convergence, or truth.
11. No external services are required.

## Boundary

Relation defines explicit links. Φ describes their structural arrangement. Later layers may evaluate resonance, convergence, meaning, or verification.
