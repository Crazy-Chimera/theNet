"""Minimal immutable local State and pure observation for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class State:
    id: str
    flow_id: str
    subject_id: str
    events: tuple[str, ...]
    version: int = 1


@dataclass(frozen=True)
class Observation:
    state_id: str
    flow_id: str
    subject_id: str
    event_count: int
    events: tuple[str, ...]
    version: int = 1


def _validate_text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty")


def _canonical(flow_id: str, subject_id: str, events: tuple[str, ...]) -> str:
    return json.dumps(
        {
            "events": events,
            "flow_id": flow_id,
            "subject_id": subject_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_state(
    flow_id: str,
    subject_id: str,
    events: tuple[str, ...] = (),
) -> State:
    _validate_text("flow_id", flow_id)
    _validate_text("subject_id", subject_id)

    if not isinstance(events, tuple):
        raise TypeError("events must be a tuple")
    if any(not isinstance(event, str) or not event.strip() for event in events):
        raise ValueError("events must contain only non-empty strings")

    identifier = sha256(
        _canonical(flow_id, subject_id, events).encode("utf-8")
    ).hexdigest()

    return State(
        id=identifier,
        flow_id=flow_id,
        subject_id=subject_id,
        events=events,
    )


def observe(state: State) -> Observation:
    return Observation(
        state_id=state.id,
        flow_id=state.flow_id,
        subject_id=state.subject_id,
        event_count=len(state.events),
        events=state.events,
        version=state.version,
    )
