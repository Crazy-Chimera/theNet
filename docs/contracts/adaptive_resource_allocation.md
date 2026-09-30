# F10.2 — Adaptive Resource Allocation

F10.2 closes the loop between verified recursive learning and future resource
allocation.

## Contract

Future memory/compute shares are derived from immutable F10.1 measurements.

Base weight: Ω-Credit

Adaptive weight: Ω-Credit × (1 + bonus) when verified_improvement = true

Otherwise: Ω-Credit

The default bonus is 0.25 and is explicitly bounded to [0, 1].

The resulting shares are normalized against the requested finite memory and
compute budgets, so the allocator cannot create resources.

## Why the signal is trusted

The adaptive bonus is not based on an agent's own claim.

It requires the F10.1 field:

verified_improvement = true

which itself requires:

- dependency on previous verified memory;
- no regression in utility, K, C, or Φ;
- strict improvement in at least one of those dimensions.

Ω-Credit and resource efficiency remain supporting observables. They are not
required to increase monotonically because resource allocation can consume
available capacity.

## Architectural loop

verified collective outcome
→ relational utility
→ Ω-Credit
→ F10.1 verified improvement
→ F10.2 adaptive weight
→ next memory/compute allocation
→ next recursive cycle

This makes resource allocation path-dependent on verified experience while
keeping resource creation and state transitions immutable.

## Safety invariants

1. Unverified cycles receive no adaptive bonus.
2. Bonus is bounded.
3. Allocation cannot exceed requested capacity.
4. Zero total credit produces zero allocation.
5. Allocation is deterministic.
6. Allocation is immutable and content-addressed.
7. F10.2 does not mutate agent code or generate goals.

## Scope

F10.2 is an operational resource-allocation mechanism. It does not establish
general intelligence, AGI, consciousness, or semantic understanding.
