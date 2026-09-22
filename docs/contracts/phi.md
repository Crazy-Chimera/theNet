# Φ Structure Contract — Iteration 5

## Purpose

Φ is the minimal structural representation of theNet: a deterministic snapshot of explicit directed relations. It captures topology without adding interpretation.

This implementation uses the source theory's structural framing—Φ describes the configuration of relations at a given state—but does not treat the theory's physical claims as experimentally established facts.

## Input

- relations: iterable of Relation objects.

## Output

An immutable PhiStructure containing:
- id
- relation_ids
- node_ids
- edges
- version = 1

## Identity

The structure ID is the SHA-256 digest of a canonical structural payload containing sorted relation IDs, derived node IDs, directed edges, and version.

Equivalent relation sets produce the same structure identity independent of input order.

## Invariants

1. Input must contain only Relation objects.
2. Empty relation collections are valid and represent an empty structure.
3. Relation IDs are unique in the resulting structure.
4. Node IDs are derived only from relation endpoints.
5. Edges preserve source-to-target direction.
6. Output is immutable.
7. Equivalent relation sets produce the same structure ID independent of input order.
8. Adding or removing a relation changes structure identity.
9. Φ does not infer meaning from a relation.
10. Φ does not verify relations.
11. Φ does not perform consensus, contribution, memory, convergence, or expression.
12. No external-service dependency.

## Boundary

Relation creates explicit links. Φ represents their structural configuration. Later modules may evaluate, remember, interpret, or evolve that configuration; Φ remains a minimal structural primitive.
