# CLI Contract — First MVP

## Purpose

Provide a deterministic, dependency-free command-line boundary for theNet primitives and the Agent Ω Genesis closure.

## Commands

### `genesis`

Creates one Genesis state.

Required:
- `--subject`
- `--created-at`

Output: JSON representation of the immutable Genesis state.

### `relation`

Creates one directed Relation.

Required:
- `--source-id`
- `--target-id`
- `--kind`
- `--created-at`

Output: JSON representation of the immutable Relation.

### `closure`

Builds the first Agent Ω Genesis closure through the existing orchestration boundary.

Required:
- `--source-subject`
- `--target-subject`
- `--relation-kind`
- `--proposal-text`
- `--evidence`
- `--expression-id`
- `--created-at`

Output: JSON object containing the closure components.

### `server`

Starts the existing HTTP runtime. This preserves the deployment boundary while making the CLI the primary module entry point.

## Invariants

1. CLI output is valid JSON for successful data commands.
2. Data commands do not mutate source objects.
3. Identical valid arguments produce identical JSON values.
4. Errors are written to stderr and return a non-zero exit code.
5. No third-party runtime dependency is introduced.
6. The CLI delegates domain logic to existing primitives; it does not duplicate identity or state-transition rules.
7. `python -m thenet --help` is usable as the discovery boundary.

## Verification

The test suite must cover:
- help/discovery
- Genesis command
- Relation command
- closure command
- invalid input failure
- deterministic output
- server command delegation boundary without starting a long-lived server
