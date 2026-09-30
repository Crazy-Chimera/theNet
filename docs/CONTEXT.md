# theNet — Living Context

## Intent

theNet is a relational network architecture in which explicit relations, immutable state transitions, memory, convergence, contribution, expression, self-modeling and safety form the basis for evolutionary collective computation.

The implementation is verified incrementally. This document is a living contract: it records the current architecture, engineering conventions, and verification boundary and must evolve with the repository.

## Current repository

- Repository: Crazy-Chimera/theNet
- Branch: main
- Runtime: Python 3.12+
- Test runner: pytest
- CI: GitHub Actions
- Deployment target: Render
- Persistence: PostgreSQL when configured; SQLite fallback for local development

The current implementation contains the foundational architecture plus collective-computation, evolution, resource, Ω-Credit, runtime, persistence and deployment layers.

## Foundational architecture

1. Genesis
2. Relation
3. Φ Structure
4. Ω Process / Pohyb
5. Ω² Memory
6. ΦΩ² Resonance
7. Γ Convergence
8. Π Meaning / Contribution
9. Ψ Expression
10. Θ Self-Knowledge
11. Ρ Relational Co-definition
12. Σ + ΙΩΤΑ Genesis Closure

Core loop:

RELATION → STATE → OBSERVE → INTERPRET → PROPOSE → SIMULATE → VERIFY → CONVERGE → COMMIT → MEMORY → LEARNING → REDEFINE SYSTEM

Central invariant:

Identity(t+1) ≈ Identity(t) + verified evolution

## Operational verification mapping

The requested six-module verification view is treated as an operational map, not as a claim that six identically named packages currently exist.

- Identita: `src/identity.py` now provides Ed25519 identity generation, deterministic `did:thenet:` identifiers, message signing/verification, and an encrypted file-backed MVP vault. Unit tests verify persistence, tampering, wrong identities/passwords, empty and large messages, invalid inputs, immutability, and absence of plaintext private keys. This is an MVP vault boundary, not a managed KMS/HSM.
- Agent: `agent_state.py`, `agent.py`, Genesis closure and collective-computation orchestration provide the current Agent Ω state/decision boundary. `run_decision_cycle()` explicitly composes Θ → Σ → Γ → Ω → Π → Ω² and can bind a proposal to the verified Ed25519 identity. The cycle is side-effect free for canonical state; verified evolution remains the only state-changing path.
- Paměť: `memory.py`, `evolution_memory.py` a `memory_store.py`; SQLiteMemoryStore nyní poskytuje explicitní episodickou, sémantickou a procedurální paměť s persistence/consistency testy.
- Síť: `thenet/server.py` provides the verified HTTP/runtime boundary. `src/network.py` now provides an Ed25519-authenticated WebSocket bootstrap/peer registry and relay, with a real loopback two-agent integration test. A production Render WebSocket endpoint is NOT YET VERIFIED because the current Render service exposes the HTTP runtime only.
- Kredit: the Ω-Credit family provides verified contribution/resource accounting, ledger/distribution/conservation gates, proportional resource allocation, and `omega_credit_account.py` for immutable Agent balances with verified earn/spend.
- Timechain: no dedicated timechain.py package is currently present. Evolution history, execution chain and commit provide the current historical/branching substrate. A full branch/rollback/prediction/merge Timechain contract is NOT VERIFIED as such.

These gaps are verification findings, not assumptions to be silently filled.

## Verification rules

Every module under verification should have:

- explicit contract;
- implementation;
- unit tests;
- negative and edge-case tests;
- deterministic/integrity tests where relevant;
- integration verification before dependent modules are accepted.

Deployment verification follows:

CI/build → tests → deployment → runtime smoke test → observation.

## Conventions

- Keep dependencies minimal.
- Prefer deterministic behavior and immutable data where practical.
- Use clear names and short functions.
- Comments explain why rather than restating what code does.
- Use “pohyb” rather than “dynamika”.
- Inspect repository state before modifying existing files.
- Do not claim a capability merely because a contract or document exists; verify executable implementation and tests.
- Do not treat passing tests as proof of physical or metaphysical claims.

## Φ-Elegance

Architectural decisions should seek:

- maximal relational utility;
- verifiability;
- continuity;
- minimal unnecessary complexity;
- minimal unnecessary dependencies.

Φ-Elegance is an engineering decision principle, not an experimentally established physical measurement.

## Verification process

For each phase:

1. inspect the actual repository;
2. compare contract → implementation → tests;
3. execute the relevant tests;
4. inspect failures and edge cases;
5. repair only verified defects;
6. rerun CI;
7. record the result and remaining gaps;
8. proceed only when the phase gate is satisfied.

The project should converge through repeated generate → test → verify → integrate → deploy → observe → learn → evolve cycles.
