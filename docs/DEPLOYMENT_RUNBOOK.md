# Deployment Runbook

## Target

Render web service: `thenet`

Repository: `Crazy-Chimera/theNet`

Branch: `main`

## Runtime

- Build: `pip install .`
- Start: `python -m thenet`
- Port: provided by `PORT`
- Health: `GET /health`

## Preconditions

1. GitHub Actions CI is green.
2. Package build succeeds.
3. Package installation succeeds.
4. Runtime smoke test returns HTTP 200 from `/health`.
5. Full test suite passes.

## Current verification baseline

The latest main commit has a successful CI run with:

- package build: success
- package installation: success
- runtime health smoke test: success
- tests: 592 passed

## Operational rule

Do not activate a suspended production service automatically. Deployment activation is a separate operational action.

## Rollback

If a deployment fails its health check, keep the previous known-good deployment active and inspect the deployment logs before retrying.
