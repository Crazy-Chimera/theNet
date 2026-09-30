# Evidence Graph Contract

## Purpose

`EvidenceGraph` is the canonical runtime projection of immutable Agent Ω artifacts.

The graph is descriptive. It does not infer truth, intelligence, consciousness, or causal claims beyond the explicit runtime relations.

## Nodes

Each node contains:
- `id` — immutable artifact identifier.
- `type` — runtime artifact class.
- `label` — human-readable runtime label.
- `payload_ref` — identifier of the source artifact.
- `version` — graph schema version.

The graph may contain `AGENT`, `STATE`, `PROPOSAL`, `VERIFICATION`, `CONSENSUS`, `CONVERGENCE`, `EXECUTION`, `OUTCOME`, `UTILITY`, `OMEGA_CREDIT`, and `MEMORY` nodes.

## Edges

Each edge contains:
- `source`
- `target`
- `relation`
- `evidence_ref`
- `version`

Relations represent explicit runtime transitions such as:
`proposes → targets → verified_by_consensus → converges → authorizes_execution → produces → measured_as → credits → remembered_as → influences`

Recursive memory dependency is represented by `informs`.

## Determinism

Nodes and edges are canonically ordered before hashing. The graph identifier is SHA-256 over the canonical graph representation.

Equivalent recursive runs therefore produce the same graph identifier when their underlying immutable artifacts are equivalent.

## Control Room boundary

The runtime constructs the graph. The UI only renders it and navigates to node identifiers.

This prevents the UI from creating an independent interpretation of runtime history.

## Safety

The graph does not:
- create new memory;
- create Ω-Credit;
- alter consensus;
- mutate AgentState;
- claim that consensus is truth;
- claim general intelligence or consciousness.

It is an observability and provenance layer.