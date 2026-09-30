"""Command-line interface for theNet MVP."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys
from typing import Sequence

from thenet.engine import build_closure
from src.genesis import create_genesis
from src.relation import create_relation


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="thenet",
        description="theNet relational computation MVP",
    )
    parser.add_argument("--version", action="version", version="0.1.0")

    commands = parser.add_subparsers(dest="command", required=True)

    genesis = commands.add_parser("genesis", help="create a Genesis state")
    genesis.add_argument("--subject", required=True)
    genesis.add_argument("--created-at", required=True)

    relation = commands.add_parser("relation", help="create a directed Relation")
    relation.add_argument("--source-id", required=True)
    relation.add_argument("--target-id", required=True)
    relation.add_argument("--kind", required=True)
    relation.add_argument("--created-at", required=True)

    closure = commands.add_parser("closure", help="build an Agent Ω Genesis closure")
    closure.add_argument("--source-subject", required=True)
    closure.add_argument("--target-subject", required=True)
    closure.add_argument("--relation-kind", required=True)
    closure.add_argument("--proposal-text", required=True)
    closure.add_argument("--evidence", required=True)
    closure.add_argument("--expression-id", required=True)
    closure.add_argument("--created-at", required=True)

    commands.add_parser("server", help="start the HTTP runtime")

    return parser


def _emit(value: object) -> None:
    print(json.dumps(asdict(value), sort_keys=True, separators=(",", ":")))


def _closure_json(closure: object) -> dict[str, object]:
    return asdict(closure)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "genesis":
            _emit(create_genesis(args.subject, args.created_at))
            return 0

        if args.command == "relation":
            _emit(
                create_relation(
                    args.source_id,
                    args.target_id,
                    args.kind,
                    args.created_at,
                )
            )
            return 0

        if args.command == "closure":
            closure = build_closure(
                source_subject=args.source_subject,
                target_subject=args.target_subject,
                relation_kind=args.relation_kind,
                proposal_text=args.proposal_text,
                evidence=args.evidence,
                expression_id=args.expression_id,
                created_at=args.created_at,
            )
            print(
                json.dumps(
                    _closure_json(closure),
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
            return 0

        if args.command == "server":
            from thenet.server import serve

            serve()
            return 0

        parser.error(f"unsupported command: {args.command}")
    except (TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 2
