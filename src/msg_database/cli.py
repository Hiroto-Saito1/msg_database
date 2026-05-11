"""Command line interface for building and querying the MSG database."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Optional, Sequence

from msg_database.builder import build_database
from msg_database.normalize import OperationKey
from msg_database.repository import MsgRepository, validate_msg_id
from msg_database.schema import connect


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "build":
            stats = build_database(args.db, msg_ids=args.msg_id)
            print(json.dumps(asdict(stats), ensure_ascii=False))
            return 0
        if args.command == "msg":
            return _query_msg(args)
        if args.command == "operation":
            return _query_operation(args)
    except (ValueError, KeyError, sqlite3.Error) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    parser.print_help(sys.stderr)
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="msg_database")
    subparsers = parser.add_subparsers(dest="command")

    build = subparsers.add_parser("build", help="build a SQLite database")
    build.add_argument("--db", type=Path, default=Path("src/msg_database.db"))
    build.add_argument(
        "--msg-id",
        type=int,
        action="append",
        help="MSG ID to include; repeat to build a subset",
    )

    msg = subparsers.add_parser("msg", help="list operations for one MSG ID")
    msg.add_argument("msg_id", type=int)
    msg.add_argument("--db", type=Path, default=Path("src/msg_database.db"))
    msg.add_argument("--format", choices=["json", "table"], default="table")

    operation = subparsers.add_parser(
        "operation",
        help="list MSG IDs containing an operation key",
    )
    operation.add_argument("--rotation", required=True)
    operation.add_argument("--translation", required=True)
    operation.add_argument("--time-reversal", type=int, choices=[0, 1], required=True)
    operation.add_argument("--db", type=Path, default=Path("src/msg_database.db"))
    operation.add_argument("--format", choices=["json", "table"], default="table")

    return parser


def _query_msg(args: argparse.Namespace) -> int:
    repo = MsgRepository(connect(args.db))
    msg_type = repo.get_msg_type(validate_msg_id(args.msg_id))
    operations = repo.find_operations_by_msg_id(args.msg_id)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "msg_type": msg_type,
                    "operations": [operation.as_dict() for operation in operations],
                },
                ensure_ascii=False,
            )
        )
    else:
        print(f"MSG {args.msg_id}: {msg_type['bns_number']}")
        for operation in operations:
            print(
                "\t".join(
                    [
                        operation.rotation_key,
                        operation.translation_key,
                        str(operation.time_reversal),
                    ]
                )
            )
    return 0


def _query_operation(args: argparse.Namespace) -> int:
    repo = MsgRepository(connect(args.db))
    operation = OperationKey(args.rotation, args.translation, args.time_reversal)
    msg_ids = repo.find_msg_ids_by_operation(operation)

    if args.format == "json":
        print(json.dumps({"msg_ids": msg_ids}, ensure_ascii=False))
    else:
        for msg_id in msg_ids:
            print(msg_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
