# Deployment Runtime Contract

## Purpose

Define the minimal production boundary for theNet. Deployment must install the package, start the runtime, expose a health endpoint, and reject malformed port configuration.

## Contract

- Package installation uses the repository pyproject.toml.
- Runtime entry point is python -m thenet.
- GET / returns JSON identifying theNet and ready status.
- GET /health returns HTTP 200 with {"status":"ready"}.
- Unknown paths return HTTP 404.
- PORT defaults to 8000.
- PORT must be an integer in 1..65535.

## Invariants

1. Build/install must succeed in a clean Python 3.12 environment.
2. Runtime health does not require external services.
3. Health responses are deterministic.
4. Invalid PORT values fail before the server starts.
5. The deployment boundary does not expose internal state or mutate domain primitives.

## Verification

CI must install the package before running tests. Runtime tests must cover health responses, unknown paths, and PORT validation.
