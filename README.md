# theNet

The Theory of Collective Computation begins with a different premise: the universe is not a program running on a fixed machine.

## Current foundation

theNet is implemented as an evolutionary relational architecture:

Genesis → Relation → Φ Structure → Ω Pohyb → Ω² Memory → ΦΩ² Resonance → Γ Convergence → Π Meaning → Ψ Expression → Θ Self-Knowledge → Ρ Co-definition → Σ / ΙΩΤΑ closure.

The implementation uses deterministic identities, immutable primitives, explicit contracts, and tests as specifications.

## Current evolution path

The Ω-Credit path now extends through distributed contribution, conservation verification, verified receipts, evolution-receipt binding, collective evolution evidence, evidence-integrity auditing, and reference-level evidence verification.

## First MVP CLI

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

Start the HTTP runtime explicitly:

~~~bash
python -m thenet server
~~~

Successful data commands emit deterministic JSON. Domain rules remain in the primitive and orchestration modules; the CLI is only the boundary.

## Basic UI

A dependency-free browser prototype is available in `ui/`.

Serve the repository locally:

~~~bash
python -m http.server 8080 --directory ui
~~~

Then open:

~~~text
http://localhost:8080
~~~

The first UI exposes:

- system overview;
- Genesis creation;
- directed Relation creation;
- local relation state;
- visible event stream.

The current UI is explicitly local/prototype state. It does not claim persistence in theNet until an API integration is added.

## Development

- Repository: Crazy-Chimera/theNet
- Branch: main
- Runtime: Python 3.12+
- Test runner: pytest
- CI: GitHub Actions

The runtime entry point is `python -m thenet`.
