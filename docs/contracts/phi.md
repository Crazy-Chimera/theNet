# Φ Structure Contract — Iteration 5

## Purpose

Φ is the minimal structural representation of theNet: a deterministic snapshot of explicit directed relations. It captures topology without adding interpretation.

The local path is:

State → Observe → Φ

Φ remains local and deterministic. It does not add consensus or distributed infrastructure.

## Input

### Direct constructor

- relations: iterable of existing Relation objects.

### Observation adapter

- observation: an existing immutable Observation.
- relations: the exact local Relation objects referenced by observation.relation_ids.

## Output

Immutable PhiStructure containing:

- id
- relation_ids
- node_ids
- edges
- version = 1

## Identity

The structure ID is the SHA-256 digest of a canonical structural payload containing sorted relation IDs, derived node IDs, directed edges, and version.

Equivalent relation sets produce the same structure identity independent of input order.

## Observation boundary

create_phi_from_observation accepts an Observation only as a local structural boundary. It checks that the supplied Relation objects exactly match observation.relation_ids, then delegates to the canonical Φ constructor.

The adapter does not trust, verify, score, or interpret the observation.

## Invariants

1. Input must contain only Relation objects.
2. Empty relation collections are valid and represent an empty structure.
3. Duplicate relation IDs are canonicalized to one structural relation rather than creating duplicate edges.
4. Node IDs are derived only from relation endpoints.
5. Edges preserve source-to-target direction.
6. Output is immutable.
7. Equivalent relation sets produce the same structure ID independent of input order.
8. Adding or removing a distinct relation changes structure identity.
9. Observation adapter rejects non-Observation input.
10. Observation adapter rejects any relation set whose IDs differ from observation.relation_ids.
11. Φ does not infer meaning from a relation.
12. Φ does not verify relations.
13. Φ does not perform consensus, contribution, memory, convergence, or expression.
14. No external-service dependency.

## Boundary

Relation creates explicit links. State materializes a local flow snapshot. Observe reads that snapshot. Φ represents the observed relation topology. Later modules may evaluate, remember, interpret, or evolve that configuration; Φ remains a minimal structural primitive.
