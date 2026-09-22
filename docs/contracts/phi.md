# Φ Structure Contract

## Purpose

Φ is the canonical structural representation of an explicit relation set. It derives a deterministic relational topology without mutating the underlying entities or relations.

## Input

A finite iterable of `Relation` objects.

## Output

An immutable `PhiStructure` containing:

- `id`: SHA-256 fingerprint of the canonical topology
- `relation_ids`: sorted unique relation identifiers
- `node_ids`: sorted unique subject identifiers appearing in the relations
- `edges`: sorted unique directed `(source_id, target_id)` pairs
- `version`: `1`

The public `create_phi` API and the canonical `create_phi_structure` API produce the same `PhiStructure` type and topology.

## Invariants

1. The input relation collection is not mutated.
2. Relation ordering does not affect the resulting structure ID.
3. Repeated relation IDs are represented once.
4. Repeated edges are represented once.
5. The same structural topology produces the same ID.
6. Changing a relation endpoint changes the topology and its ID.
7. Reversing a directed relation changes the topology and its ID.
8. An empty relation collection is valid and produces an empty structural state.
9. The output is immutable.
10. Φ does not verify relations, establish consensus, infer meaning, allocate resources, or mutate memory.
11. No external service is required.

## Boundary

Genesis creates subjects. Relation creates directed links. Φ represents their canonical topology. Φ-derived coherence may measure structural connectedness, but verification, convergence, meaning, memory, expression, self-knowledge and co-definition remain later concerns.
