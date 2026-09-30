# Evidence Graph Query Contract

## Purpose

The Evidence Graph Query Layer provides deterministic traversal over the canonical Evidence Graph. It is an inspection and audit primitive, not a second source of runtime truth.

## Operations

`POST /v1/control/query` accepts:

- `operation=query` (default): bounded neighborhood traversal from `node_id`.
- `operation=path`: deterministic path search from `source_id` to `target_id`.

Supported traversal directions:

- `forward`
- `backward`
- `both`

Optional filters for neighborhood queries:

- `relation`
- `node_type`
- `max_depth`

## Invariants

1. The query layer never mutates the Evidence Graph.
2. Traversal is deterministic through canonical edge ordering.
3. Traversal is bounded by `max_depth`.
4. Path results preserve the ordered runtime evidence edges.
5. The API returns the source graph identifier.
6. The query layer cannot create consensus, credit, memory, state, or execution artifacts.

## Audit Example

A recursive computation can therefore be traced as:

`PROPOSAL → CONSENSUS → CONVERGENCE → EXECUTION → OUTCOME → MEMORY`

The returned path is an inspection projection of existing immutable runtime artifacts.

This contract does not establish AGI, consciousness, truth, or intelligence. It establishes a deterministic mechanism for querying and auditing relationships that the runtime has already produced.