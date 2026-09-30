# Basic UI

## Purpose

The first theNet user interface is a dependency-free browser surface for observing and interacting with the foundational model.

It exposes:

- system status;
- Genesis creation;
- relation creation;
- the current local relation graph;
- an event stream for visible state changes.

## Boundary

This UI is a prototype surface. It does not replace the domain modules in `src/`.

Until an HTTP/API layer exists, actions are executed in browser memory only.

The UI therefore must not claim that a Genesis or Relation has been persisted by the theNet runtime.

## Design

The interface is intentionally small:

```
UI
├── System
├── Genesis
├── Relations
└── Event stream
```

The visual language follows theNet terminology:

```
Genesis → Relation → State
```

Future integration should replace the local action handlers with calls to theNet services while preserving the same UI contracts.
