# Φ Structure Interface — Iteration 5

## Purpose

Φ Structure is the first aggregate structural layer above the primitive Relation.

It represents a deterministic snapshot of a relational network: the participating node identities, the directed relations connecting them, and a derived structural density value Φ.

The implementation is intentionally computational and network-oriented. The Φ theory source describes Φ as a measure of relational/entanglement density; this interface does not claim that the software measurement is a physical measurement of quantum entanglement.

## Source basis

The source text defines:
- Φ as Structure — a description of how entities are connected.
- An informion as information about a relationship between two nodes.
- Φ as a density-like quantity over relationships.
- In the internet adaptation, Φ_net can be approximated from the number and strength of connections.
- Φ is static structure; Ω is reserved for change/process.

For theNet, this becomes a minimal structural snapshot over explicit Relation primitives.

## Input

`create_structure(relations)`

- `relations`: finite iterable of `Relation` values.
- Every relation must contain non-empty `source_id` and `target_id`.
- Relation IDs must be unique within the snapshot.
- The same relation may not be supplied twice.

## Output

An immutable `PhiStructure`:
- `id: str`
- `nodes: tuple[str, ...]`
- `relations: tuple[Relation, ...]`
- `phi: float`
- `version: int = 1`

### `nodes`

The unique node IDs referenced by the relation set, returned in deterministic lexical order.

### `relations`

The supplied relations, returned in deterministic order by relation ID.

### `phi`

A normalized structural density for the finite directed graph:

`Φ = |E| / (|V| · (|V| - 1))`

where:
- `V` is the number of unique nodes.
- `E` is the number of unique directed relations.
- self-relations are rejected because they do not represent a directed connection between distinct nodes in this MVP metric.

For a graph with fewer than two nodes, `Φ = 0.0`.

This is theNet's MVP structural approximation of Φ, not the physical equation `Φ = (1/V) · Σ I(A:B)` from the source text.

## Identity

`id` is the SHA-256 digest of a canonical structure payload containing:
- `nodes`
- canonical relation IDs
- `phi`
- `version`

The canonical representation must be deterministic.

Equivalent relation sets must therefore produce the same structure ID regardless of input order.

## Invariants

1. The structure is immutable.
2. Empty relation input produces an empty structure with `nodes = ()`, `relations = ()`, and `phi = 0.0`.
3. Every relation ID is unique inside a structure.
4. Nodes are derived only from relation endpoints.
5. Nodes are deterministic and sorted.
6. Relations are deterministic and sorted.
7. Input order does not change the structure identity.
8. `0.0 <= phi <= 1.0`.
9. `phi` depends only on the unique directed relation set and its node set.
10. Structure creation does not mutate any Relation.
11. No external service is required.
12. Φ Structure does not perform process evolution, memory, consensus, verification, contribution scoring, meaning, or self-modification.
13. Ω/process remains a later layer and must not be introduced into this module.

## Boundary

- Genesis creates initial entities.
- Relation creates explicit directed links.
- Φ Structure aggregates those links into a deterministic structural snapshot.
- Ω will later describe change between structural snapshots.
- Ω² will later persist structural/process traces.

The Φ module must remain independent of Ω, Ω², consensus, storage, network transport, and external services.

## Failure cases

Construction must reject:
- non-Relation values;
- duplicate relation IDs;
- self-relations for the MVP structural density;
- invalid Relation objects that violate the Relation contract.

The module should fail explicitly rather than silently deduplicating or rewriting invalid input.

## Required tests

The test suite must verify:
- empty structure;
- one relation;
- node extraction;
- deterministic ordering;
- deterministic identity;
- input-order independence;
- density calculation;
- duplicate relation rejection;
- self-relation rejection;
- invalid input rejection;
- output immutability;
- no mutation of source Relation values.

## Verification target

CI must run the complete repository test suite after implementation.

The Φ Structure implementation is complete only when the new tests and all existing tests pass.
