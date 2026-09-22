# Γ Convergence Contract

## Purpose

Γ is the minimal convergence primitive. It records a deterministic selection from a finite set of candidate state identifiers after an external verification process has established which candidate may be selected.

Γ does not perform voting, verification, optimization, or consensus itself. It records the converged result and its candidate set.

## Input

- `candidates`: finite iterable of non-empty state identifiers.
- `selected_state`: non-empty state identifier contained in `candidates`.
- `created_at`: non-empty convergence timestamp.

## Output

Immutable `Convergence`:

- `id`: SHA-256 identity of canonical convergence payload.
- `candidate_states`: sorted unique tuple of candidate state identifiers.
- `selected_state`: selected candidate.
- `created_at`
- `version`: 1.

## Canonicalization

Candidate order does not affect identity. Duplicate candidate identifiers collapse to one structural candidate.

## Invariants

1. Candidates must be a finite iterable of non-empty strings.
2. At least one candidate is required.
3. `selected_state` must belong to the canonical candidate set.
4. Output is immutable.
5. Equivalent candidate sets with the same selection and timestamp produce the same identity.
6. Changing the candidate set, selected state, or timestamp changes identity.
7. No input collection is mutated.
8. Γ does not establish that the selected state is objectively correct.
9. Γ does not itself perform consensus or verification.
10. No external service or global state is required.

## Boundary

Φ describes structure. Ω records pohyb. Ω² retains memory. ΦΩ² relates structure and memory. Γ records the result of a separately established convergence decision. Later Π may interpret the converged result as contribution/meaning, while Ψ may express it as an action or commit.
