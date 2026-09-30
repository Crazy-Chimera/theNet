# Φ Structure Interface — Iteration 5

## Purpose

Φ Structure is the structural layer after Relation. It derives a deterministic structural fingerprint from explicit relations without changing those relations or asserting semantic truth.

The source Φ text describes Φ as Structure: relationships are primary, and the structure of a network is determined by how its relational units are connected. In theNet, this is implemented as a deterministic graph/fingerprint representation over explicit Relation primitives.

This software representation is an engineering model inspired by the source terminology; it is not presented as a physical measurement of quantum entanglement.

## Input

`create_phi_structure(relations)`

- `relations`: an iterable of `Relation` objects.
- Required Relation fields: `id`, `source_id`, `target_id`.

Compatibility alias:

`create_structure(relations)`

## Output

An immutable `PhiStructure` containing:

- `id`
- `relation_ids`
- `node_ids`
- `edges`: ordered `(source_id, target_id)` pairs
- `version = 1`
- `edge_count`: derived property
- `node_count`: derived property

The canonical implementation lives in `src/structure.py`. `src/phi_structure.py` is a compatibility entry point.

## Identity

The structure ID is SHA-256 over canonical:

- relation IDs
- node IDs
- edges
- version

Duplicate occurrences of the same Relation ID are collapsed deterministically. Input order does not affect the resulting structure identity.

## Invariants

1. Empty relation collections are valid.
2. Inputs must contain only Relation objects.
3. Duplicate Relation IDs are deduplicated deterministically.
4. Input order does not affect identity.
5. Output is immutable.
6. Source Relation objects are not mutated.
7. Node IDs are derived only from relation endpoints and returned in sorted order.
8. Edges are ordered according to the sorted unique Relation IDs.
9. `edge_count` equals the number of structural edges.
10. `node_count` equals the number of structural nodes.
11. Φ Structure does not claim verification, consensus, contribution, meaning, memory, convergence, or truth.
12. No external services are required.
13. Φ Structure describes a static structural snapshot; process/change belongs to Ω.

## Boundary

- Genesis creates entities.
- Relation defines explicit links.
- Φ Structure describes their structural arrangement.
- Ω will later describe change between structural states.
- Ω² will later persist structural/process traces.

The module remains independent of consensus, storage, network transport, and external services.

## Required tests

The repository must verify:

- empty relation collection;
- one or more relations;
- unique sorted node extraction;
- deterministic ordering;
- input-order independence;
- deterministic identity;
- duplicate Relation-ID handling;
- changed relation identity;
- immutability;
- invalid Relation rejection;
- source Relation immutability;
- generator input support.

## Verification target

The complete repository test suite must pass in CI after the interface and implementation state are committed.
