# ΙΩΤΑ Unity Contract

## Purpose

ΙΩΤΑ is the singularity/unity closure of the architecture. The source framework describes it as the recognition that all layers are one: the unity of Φ, Ω, Ω², ΦΩ², Γ, Π, Ψ, Θ, Ρ, and Σ.

For theNet, ΙΩΤΑ is implemented as an explicit immutable closure over one reference to each completed layer. This is a software representation of architectural unity, not a claim that the source framework's physical or metaphysical equations are experimentally established.

## Input

Ten non-empty layer identifiers:

- `phi_id`
- `omega_id`
- `omega2_id`
- `resonance_id`
- `gamma_id`
- `pi_id`
- `psi_id`
- `theta_id`
- `rho_id`
- `sigma_id`

Plus a non-empty `created_at` timestamp.

## Output

An immutable `Singularity`:

- `id`
- all ten layer identifiers
- `created_at`
- `version = 1`

## Identity

The ID is SHA-256 over canonical JSON containing all ten layer identifiers, timestamp, and version.

Changing any defining layer reference changes the ΙΩΤΑ identity.

## Invariants

1. Every layer identifier and timestamp must be a non-empty string.
2. All ten architectural components are required for closure.
3. Same inputs produce the same ID.
4. Changing any defining input changes the ID.
5. The result is immutable.
6. Inputs are not mutated.
7. No external services are required.
8. ΙΩΤΑ does not infer that the referenced layers are true or correct.
9. ΙΩΤΑ does not mutate any referenced layer.
10. ΙΩΤΑ is an architectural unity closure, not a numerical claim that unity has physically reached 1.

## Boundary

- Φ, Ω, Ω², ΦΩ², Γ, Π, Ψ, Θ, Ρ, and Σ provide the ten layer references.
- ΙΩΤΑ binds them into one explicit architectural state.
- Later Agent Ω orchestration can use this closure as the foundational invariant for collective computation.
