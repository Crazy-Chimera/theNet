# Runtime HTTP / API Contract

## Purpose

The HTTP runtime is the external boundary of theNet. It exposes deterministic health and identity endpoints plus JSON endpoints for Genesis, Relation, and closure execution.

The HTTP layer is an adapter; domain rules remain in the primitive and orchestration modules.

## Transport

- HTTP/1.1.
- JSON request and response bodies for API routes.
- \`Content-Type: application/json\` is required for POST requests.
- Bind address: \`0.0.0.0\`.
- Port: \`PORT\` when supplied by the hosting platform; otherwise \`8000\`.
- \`PORT\` must be an integer in \`1..65535\`.

## Common response rules

Successful routes return HTTP \`200\` and a JSON object.

Invalid JSON, missing required fields, wrong content type, empty required strings, or other request-shape violations return HTTP \`400\`:

\`\`\`json
{"error":"<message>"}
\`\`\`

Unsupported paths return HTTP \`404\`:

\`\`\`json
{"status":"not_found"}
\`\`\`

## Endpoint contract

| Method | Path | Request | Success |
|---|---|---|---|
| GET | \`/health\` | none | \`{"status":"ready"}\` |
| GET | \`/\` | none | \`{"service":"theNet","status":"ready"}\` |
| POST | \`/v1/genesis\` | Genesis JSON | serialized \`GenesisState\` |
| POST | \`/v1/relations\` | Relation JSON | serialized \`Relation\` |
| POST | \`/v1/closure\` | Closure JSON | serialized closure |

## GET /health

No request body.

HTTP \`200\`:

\`\`\`json
{"status":"ready"}
\`\`\`

The endpoint is intended for platform health checks and smoke tests. It does not execute an evolutionary state transition.

## GET /

No request body.

HTTP \`200\`:

\`\`\`json
{"service":"theNet","status":"ready"}
\`\`\`

## POST /v1/genesis

### Request schema

\`\`\`json
{
  "subject": "string, non-empty",
  "created_at": "string, non-empty"
}
\`\`\`

### Response schema

\`\`\`json
{
  "id": "sha256 hex string",
  "subject": "string",
  "created_at": "string",
  "relations": [],
  "version": 1
}
\`\`\`

The identity is deterministic for the same valid \`subject\` and \`created_at\`.

## POST /v1/relations

### Request schema

\`\`\`json
{
  "source_id": "string, non-empty",
  "target_id": "string, non-empty",
  "kind": "string, non-empty",
  "created_at": "string, non-empty"
}
\`\`\`

### Response schema

\`\`\`json
{
  "id": "sha256 hex string",
  "source_id": "string",
  "target_id": "string",
  "kind": "string",
  "created_at": "string",
  "version": 1
}
\`\`\`

The relation is directed. Reversing \`source_id\` and \`target_id\` changes its deterministic identity.

## POST /v1/closure

### Request schema

\`\`\`json
{
  "source_subject": "string, non-empty",
  "target_subject": "string, non-empty",
  "relation_kind": "string, non-empty",
  "proposal_text": "string, non-empty",
  "evidence": "string, non-empty",
  "expression_id": "string, non-empty",
  "created_at": "string, non-empty"
}
\`\`\`

### Response

The response is the serialized closure object produced by \`thenet.engine.build_closure\`. Its exact fields are owned by the closure/domain contract rather than by the HTTP adapter.

## Error contract

Missing or invalid required data:

\`\`\`json
{"error":"<validation message>"}
\`\`\`

Wrong content type:

\`\`\`json
{"error":"Content-Type must be application/json"}
\`\`\`

Invalid JSON:

\`\`\`json
{"error":"request body must be valid JSON"}
\`\`\`

Unsupported path:

\`\`\`json
{"status":"not_found"}
\`\`\`

## Runtime invariants

1. Startup does not require an external service.
2. \`GET /health\` is deterministic and side-effect free.
3. Health checks do not perform evolutionary state transitions.
4. The runtime remains alive after startup.
5. POST validation is delegated to theNet primitives and orchestration modules.
6. JSON output uses deterministic key ordering and compact separators.
7. The HTTP adapter remains dependency-free and uses Python standard-library components only.

## Verification

CI verifies package installation, the complete pytest suite, and a live Render smoke request:

\`\`\`bash
curl --fail --silent --show-error --retry 10 --retry-delay 3 --retry-all-errors \\
  https://thenet-eew6.onrender.com/health
\`\`\`

Expected body:

\`\`\`json
{"status":"ready"}
\`\`\`
