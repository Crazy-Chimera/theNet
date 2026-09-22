# Runtime HTTP Contract

## Purpose

The deployment runtime must remain alive as a web service and expose a minimal health boundary for platform orchestration.

## Input

- Environment variable PORT when supplied by the hosting platform.
- Otherwise port 8000 for local execution.

## Behavior

- Bind to 0.0.0.0.
- Serve GET /health with HTTP 200 and JSON status ready.
- Serve GET / with HTTP 200 and a concise runtime identity.
- Return HTTP 404 for unsupported paths.
- Use only Python standard-library components.
- Keep the process alive until interrupted.

## Invariants

1. Startup does not require external services.
2. The health endpoint is deterministic.
3. The runtime does not execute evolutionary state transitions merely by being healthy.
4. The runtime process remains alive after startup.
5. PORT is validated as a positive integer.
