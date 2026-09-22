# Φ Structure Contract — Iteration 5

## Purpose

Φ is the minimal structural representation of theNet: a deterministic snapshot of explicit relations without adding interpretation, scoring, convergence, memory, or meaning.

## Input

- relations: iterable of Relation-compatible records.
- Each relation must expose id, source_id, target_id, kind, created_at, and version.

## Output

An immutable Structure containing:
- id
- relation_ids
- version = 1

## Identity

id is the SHA-256 digest of the canonical ordered structure payload. Relation IDs are normalized into a sorted tuple so equivalent relation sets produce the same structure identity.

## Invariants

1. Input relations must be structurally valid.
2. Empty relation collections are valid and represent an empty structure.
3. Relation IDs are unique in the resulting structure.
4. Output is immutable.
5. Equivalent relation sets produce the same structure ID independent of input order.
6. Adding or removing a relation changes structure identity.
7. Φ does not infer meaning from a relation.
8. Φ does not verify relations.
9. Φ does not perform consensus, contribution, memory, convergence, or expression.
10. No external-service dependency.

## Boundary

Relation creates explicit links. Φ represents their structural configuration. Later modules may evaluate, remember, interpret, or evolve that configuration; Φ remains a minimal structural primitive.
