# theNet MVP 0.1

The Theory of Collective Computation begins with a different premise: the universe is not a program running on a fixed machine.

## Public runtime

The current MVP is a publicly running Python service with:

- browser UI;
- HTTP API;
- deterministic Genesis and Relation primitives;
- in-process runtime state;
- first Agent Ω Genesis Closure execution.

Public service:

https://thenet-eew6.onrender.com

Health:

https://thenet-eew6.onrender.com/health

State:

https://thenet-eew6.onrender.com/v1/state

The current MVP runtime state is process-local and therefore ephemeral across service restarts. Persistent relational memory belongs to the next storage iteration.

## Architecture

Genesis → Relation → Φ Structure → Ω Pohyb → Ω² Memory → ΦΩ² Resonance → Γ Convergence → Π Meaning → Ψ Expression → Θ Self-Knowledge → Ρ Co-definition → Σ / ΙΩΤΑ closure.

The Agent Ω Genesis Closure composes:

Genesis → Relation → Φ → Ω → Ω² → ΦΩ² → Γ → Π → Ψ → Θ → Ρ → Σ → ΙΩΤΑ → Agent Ω state.

This software composition is an implementation of the project's architectural model; it does not establish the physical or metaphysical claims of the source framework.

## HTTP API

### Health

~~~http
GET /health
~~~

### Runtime state

~~~http
GET /v1/state
~~~

### Genesis

~~~http
POST /v1/genesis
Content-Type: application/json

{"subject":"alpha","created_at":"2026-09-30T00:00:00Z"}
~~~

### Relation

~~~http
POST /v1/relations
Content-Type: application/json

{"source_id":"alpha","target_id":"beta","kind":"supports","created_at":"2026-09-30T00:00:00Z"}
~~~

### Agent Ω Genesis Closure

~~~http
POST /v1/closure
Content-Type: application/json

{
  "source_subject":"Agent Ω",
  "target_subject":"theNet",
  "relation_kind":"computes",
  "proposal_text":"Advance verified relational state.",
  "evidence":"Deterministic MVP verification.",
  "expression_id":"mvp-expression",
  "created_at":"2026-09-30T00:00:00Z"
}
~~~

The closure response exposes the complete composed layer state, including the ΙΩΤΑ and Agent Ω state identities.

## CLI

The primary module entry point is:

~~~bash
python -m thenet --help
~~~

Create a Genesis state:

~~~bash
python -m thenet genesis \
  --subject alpha \
  --created-at 2026-09-30T00:00:00Z
~~~

Create a directed Relation:

~~~bash
python -m thenet relation \
  --source-id alpha \
  --target-id beta \
  --kind supports \
  --created-at 2026-09-30T00:00:00Z
~~~

Build the first Agent Ω Genesis closure:

~~~bash
python -m thenet closure \
  --source-subject alpha \
  --target-subject beta \
  --relation-kind supports \
  --proposal-text "test proposal" \
  --evidence "test evidence" \
  --expression-id expr-1 \
  --created-at 2026-09-30T00:00:00Z
~~~

Start the HTTP runtime:

~~~bash
python -m thenet server
~~~

## Development

- Repository: Crazy-Chimera/theNet
- Branch: main
- Runtime: Python 3.12+
- Test runner: pytest
- CI: GitHub Actions
- Deployment: Render
