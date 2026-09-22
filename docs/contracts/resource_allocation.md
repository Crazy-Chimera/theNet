# Resource-Aware Ω-Credit Allocation Contract

## Purpose

This integration layer combines verified Ω-Credit with a local Resource State. It converts contribution signals into a deterministic allocation plan bounded by the currently unconsumed local capacity.

It is a planning primitive. It does not transfer, reserve, or execute resources.

## Rule

Given Resource State with available capacity A and used amount U:

remaining_capacity = max(A - U, 0)

Then apply the existing Ω-Credit proportional allocation rule over verified positive credits.

The credit signal already contains:
- verified relational utility
- resource efficiency
- Φ-derived coherence

Therefore this layer does not recompute those signals.

## Output

Immutable allocation entries with:
- contributor_id
- credit
- allocation
- version

## Invariants

1. Resource State must be a ResourceState instance.
2. Credits must be OmegaCredit values.
3. Only verified positive credit contributes.
4. Allocation is bounded by remaining local capacity.
5. If remaining capacity is zero, every allocation is zero.
6. The same inputs produce the same allocation.
7. No credit or Resource State object is mutated.
8. No external service is required.
9. The result is a planning signal, not a resource transfer.
10. Local allocation does not require network-wide majority consensus.

## Architectural role

verified relational utility + resource state + Φ-derived coherence
→ Ω-Credit
→ remaining local capacity
→ self-organizing allocation signal

The primitive is deliberately local. Global consensus, permission, and execution remain separate layers.
