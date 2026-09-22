# Resource State Contract

## Purpose

Resource State is the local, immutable description of computational capacity available to an Agent Ω for an allocation cycle. It provides a deterministic efficiency signal that Ω-Credit can consume without directly controlling infrastructure.

## Input

- `available`: finite non-negative resource capacity.
- `used`: finite non-negative resource consumption.
- `created_at`: non-empty string.

## Output

Immutable `ResourceState`:

- `id`
- `available`
- `used`
- `efficiency`
- `created_at`
- `version=1`

## Efficiency rule

When `available > 0`:

`efficiency = min(used / available, 1)`

When `available = 0`:

`efficiency = 0`

This is a normalized local signal, not a claim about global resource quality.

## Invariants

1. Numeric inputs must be finite numbers.
2. `available` and `used` must be non-negative.
3. `created_at` must be non-empty.
4. The output is immutable.
5. The same valid input produces the same ID and efficiency.
6. Input values are not mutated.
7. Efficiency is bounded to [0, 1].
8. Resource State does not allocate, transfer, or reserve resources.
9. Resource State does not establish verification, consensus, meaning, or permission to commit.
10. No external service is required.

## Architectural boundary

`resource observation → Resource State → efficiency signal → Ω-Credit → allocation signal`

Actual resource transfer remains outside this primitive.
