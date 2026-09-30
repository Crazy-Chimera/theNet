"""Immutable local State snapshot and pure observation for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from src.user_flow import UserFlow


@dataclass(frozen=True)
class State:
    id: str
    flow_id: str
    context_id: str
    subject_id: str
    stage: str
    relation_ids: tuple[str, ...]
    version: int = 1


@dataclass(frozen=True)
class Observation:
    state_id: str
    flow_id: str
    subject_id: str
    stage: str
    relation_count: int
    relation_ids: tuple[str, ...]
    version: int = 1


def _canonical(flow: UserFlow) -> str:
    payload = {
        "context_id": flow.context.id,
        "flow_id": flow.id,
        "relation_ids": tuple(relation.id for relation in flow.context.relations),
        "stage": flow.stage,
        "subject_id": flow.context.genesis.subject,
        "version": 1,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def create_state(flow: UserFlow) -> State:
    if not isinstance(flow, UserFlow):
        raise TypeError("flow must be a UserFlow")

    relation_ids = tuple(relation.id for relation in flow.context.relations)
    identifier = sha256(_canonical(flow).encode("utf-8")).hexdigest()

    return State(
        id=identifier,
        flow_id=flow.id,
        context_id=flow.context.id,
        subject_id=flow.context.genesis.subject,
        stage=flow.stage,
        relation_ids=relation_ids,
    )


def observe(state: State) -> Observation:
    if not isinstance(state, State):
        raise TypeError("state must be a State")

    return Observation(
        state_id=state.id,
        flow_id=state.flow_id,
        subject_id=state.subject_id,
        stage=state.stage,
        relation_count=len(state.relation_ids),
        relation_ids=state.relation_ids,
    )
