"""Immutable local UserFlow and RequestContext orchestration primitives."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from src.genesis import GenesisState, create_genesis
from src.relation import Relation


@dataclass(frozen=True)
class RequestContext:
    id: str
    request_id: str
    created_at: str
    genesis: GenesisState
    relations: tuple[Relation, ...]
    version: int = 1

    @property
    def participants(self) -> frozenset[str]:
        participants = {self.genesis.id}
        for relation in self.relations:
            participants.add(relation.source_id)
            participants.add(relation.target_id)
        return frozenset(participants)


@dataclass(frozen=True)
class UserFlow:
    id: str
    context: RequestContext
    stage: str
    version: int = 1


def _context_id(
    request_id: str,
    created_at: str,
    genesis_id: str,
    relations: tuple[Relation, ...],
) -> str:
    payload = {
        "created_at": created_at,
        "genesis_id": genesis_id,
        "relations": [relation.id for relation in relations],
        "request_id": request_id,
        "version": 1,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _flow_id(context_id: str, stage: str) -> str:
    payload = {
        "context_id": context_id,
        "stage": stage,
        "version": 1,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def create_request_context(
    request_id: str,
    created_at: str,
    genesis: GenesisState,
    relations: tuple[Relation, ...] = (),
) -> RequestContext:
    if not isinstance(request_id, str) or not request_id.strip():
        raise ValueError("request_id must be non-empty")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")
    if not isinstance(genesis, GenesisState):
        raise TypeError("genesis must be a GenesisState")
    if not isinstance(relations, tuple):
        raise TypeError("relations must be a tuple")

    for relation in relations:
        if not isinstance(relation, Relation):
            raise TypeError("relations must contain only Relation values")

    identifier = _context_id(
        request_id,
        created_at,
        genesis.id,
        relations,
    )
    return RequestContext(
        id=identifier,
        request_id=request_id,
        created_at=created_at,
        genesis=genesis,
        relations=relations,
    )


def start_user_flow(
    request_id: str,
    subject: str,
    created_at: str,
) -> UserFlow:
    genesis = create_genesis(subject=subject, created_at=created_at)
    context = create_request_context(
        request_id=request_id,
        created_at=created_at,
        genesis=genesis,
    )
    return UserFlow(
        id=_flow_id(context.id, "GENESIS"),
        context=context,
        stage="GENESIS",
    )


def add_relation(flow: UserFlow, relation: Relation) -> UserFlow:
    if not isinstance(flow, UserFlow):
        raise TypeError("flow must be a UserFlow")
    if not isinstance(relation, Relation):
        raise TypeError("relation must be a Relation")

    if not (
        relation.source_id in flow.context.participants
        or relation.target_id in flow.context.participants
    ):
        raise ValueError("relation is not connected to the current context")

    relations = flow.context.relations + (relation,)
    context = create_request_context(
        request_id=flow.context.request_id,
        created_at=flow.context.created_at,
        genesis=flow.context.genesis,
        relations=relations,
    )
    return UserFlow(
        id=_flow_id(context.id, "RELATION"),
        context=context,
        stage="RELATION",
    )
