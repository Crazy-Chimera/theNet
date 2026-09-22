# Φ-Derived Coherence Contract

## Purpose

Φ-derived coherence is a bounded structural signal calculated only from a Φ relational structure. It is an engineering metric for downstream contribution and allocation logic; it is not a truth score, consensus score, or physical law.

## Rule — version 1

For a non-empty relational structure:

- construct an undirected connectivity view from the structure's relation endpoints;
- find the largest connected component;
- coherence = largest_component_size / node_count.

Therefore:

- empty structure → 0.0
- a fully connected relational component → 1.0
- disconnected components → proportional coverage of the largest component.

## Invariants

1. Result is finite and in [0, 1].
2. The input Φ structure is not mutated.
3. Repeated calculation is deterministic.
4. Relation ordering does not affect coherence.
5. Duplicate relations do not affect coherence because Φ canonicalizes relation IDs.
6. A disconnected structure cannot receive full coherence.
7. Coherence is structural only; it does not establish truth, verification, consensus, meaning, or permission to commit.
8. No external service is required.

## Architectural role

Relation → Φ Structure → Φ coherence → Ω-Credit

This signal can be combined with verified relational utility and resource efficiency. It does not replace verification.
