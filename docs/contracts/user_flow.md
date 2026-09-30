# UserFlow / RequestContext Contract

## Purpose

RequestContext is the immutable local execution context of one theNet request. UserFlow is the immutable flow wrapper that evolves that context through explicit local steps.

This layer connects Genesis and Relation without introducing distributed infrastructure. It provides the boundary on which later layers can attach observation, interpretation, proposal, verification, convergence, memory and expression.

## RequestContext

### Input

- request_id: non-empty string identifying the request scope.
- created_at: non-empty string.
- genesis: an existing GenesisState.
- relations: zero or more existing immutable Relation values.

### Output

Immutable RequestContext containing:

- id
- request_id
- created_at
- genesis
- relations
- version=1

id is deterministic from the request scope, Genesis identity and ordered relation identities.

### Invariants

1. request_id and created_at must be non-empty strings.
2. genesis must be a GenesisState.
3. Every relation must be a Relation.
4. Relation order is explicit and contributes to context identity.
5. The context does not mutate Genesis or Relation.
6. The context does not perform network, storage, consensus or distributed verification.
7. Creating a context with identical inputs produces the same id.
8. Adding a relation creates a new context rather than mutating the existing context.
9. A relation added through the flow must reference the context Genesis or an already-known relation participant.
10. Context construction does not imply that a relation is verified, trusted, meaningful or globally agreed.

## UserFlow

### Input

A RequestContext plus explicit local flow steps.

### Output

Immutable UserFlow containing:

- id
- context
- stage
- version=1

Initial stage is GENESIS.

Allowed stages in this iteration:

GENESIS → RELATION

Later stages may extend the vocabulary without changing the existing primitives.

### Operations

- start_user_flow(...) creates Genesis and the initial RequestContext.
- add_relation(flow, relation) returns a new flow whose context contains the relation and whose stage is RELATION.

### Invariants

1. Flow operations are deterministic.
2. Flow operations do not mutate prior flow/context instances.
3. A relation can only be added when it is structurally connected to the context.
4. No operation performs distributed consensus or external I/O.
5. UserFlow is orchestration state, not a claim about global system state.

## Boundary to future layers

The flow is deliberately narrow:

Request → RequestContext → UserFlow → [future layers]

Future layers may consume the same immutable context and append their own state without requiring a redesign of Genesis or Relation.

The contract does not define verification, contribution, memory, convergence, meaning or expression. Those remain separate modules.
