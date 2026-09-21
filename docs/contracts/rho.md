# Ρ Relational Co-Definition Contract

## Purpose

Ρ is the relational co-definition layer. It records an explicit relationship in which two self-model references jointly define a relational context.

Ρ does not infer agreement, truth, consensus, identity equivalence, or meaning. It makes co-definition explicit and deterministic.

## Input

- `left_id`: non-empty self-model identifier.
- `right_id`: non-empty self-model identifier.
- `relation_kind`: non-empty relation label.
- `created_at`: non-empty timestamp.

## Output

An immutable `RelationalCoDefinition`:

- `id`
- `left_id`
- `right_id`
- `relation_kind`
- `created_at`
- `version = 1`

## Identity

The ID is SHA-256 over canonical JSON containing all defining inputs plus version.

The relation is directional: swapping `left_id` and `right_id` changes the identity.

## Invariants

1. All defining values must be non-empty strings.
2. Same input produces the same ID.
3. Changing any defining input changes the ID.
4. Reversing the two endpoints changes the ID.
5. The result is immutable.
6. Inputs are not mutated.
7. No external services are required.
8. Ρ does not mutate either referenced self-model.
9. Ρ does not establish verification, consensus, truth, meaning, or contribution.
10. Co-definition is explicit; it is not inferred from mere coexistence.

## Boundary

- Θ provides explicit self-model references.
- Ρ connects self-model references into a co-defined relational context.
- Later convergence and expression layers may use Ρ as an input.
