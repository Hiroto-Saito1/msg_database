"""MSG DB を生成・検索するための CLI。

このモジュールは引数解析と標準入出力だけを担当し、実処理は builder/queries に
委譲する。
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from msg_database.builder import build_database
from msg_database.domain import OperationKey
from msg_database.queries import (
    find_msg_ids_by_operation,
    get_database_metadata,
    get_msg_record,
)


DEFAULT_DB = Path("data/generated/msg_database.sqlite")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint。成功時は 0、入力や DB の問題は 2 を返す。"""

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
        if args.command == "metadata":
            return _query_metadata(args)
    except (ValueError, KeyError, sqlite3.Error) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    parser.print_help(sys.stderr)
    return 2


def build_parser() -> argparse.ArgumentParser:
    """サブコマンドを含む argparse parser を組み立てる。"""

    parser = argparse.ArgumentParser(prog="msg_database")
    subparsers = parser.add_subparsers(dest="command")

    build = subparsers.add_parser("build", help="build a SQLite database")
    build.add_argument("--db", type=Path, default=DEFAULT_DB)
    build.add_argument(
        "--msg-id",
        type=int,
        action="append",
        help="MSG ID to include; repeat to build a subset",
    )

    msg = subparsers.add_parser("msg", help="list operations for one MSG ID")
    msg.add_argument("msg_id", type=int)
    msg.add_argument("--db", type=Path, default=DEFAULT_DB)
    msg.add_argument("--format", choices=["json", "table"], default="table")

    operation = subparsers.add_parser(
        "operation",
        help="list MSG IDs containing an operation key",
    )
    operation.add_argument("--rotation", required=True)
    operation.add_argument("--translation", required=True)
    operation.add_argument("--time-reversal", type=int, choices=[0, 1], required=True)
    operation.add_argument("--db", type=Path, default=DEFAULT_DB)
    operation.add_argument("--format", choices=["json", "table"], default="table")

    metadata = subparsers.add_parser("metadata", help="show database metadata")
    metadata.add_argument("--db", type=Path, default=DEFAULT_DB)
    metadata.add_argument("--format", choices=["json", "table"], default="table")

    return parser


def _query_msg(args: argparse.Namespace) -> int:
    """MSG ID から operation 一覧を出力する。"""

    record = get_msg_record(args.db, args.msg_id)

    if args.format == "json":
        print(json.dumps(record.as_dict(), ensure_ascii=False))
    else:
        print(f"MSG {args.msg_id}: {record.msg_type.bns_number}")
        for operation in record.operations:
            print(
                "\t".join(
                    [
                        operation.rotation_key,
                        operation.translation_key,
                        str(operation.time_reversal_int),
                    ]
                )
            )
    return 0


def _query_operation(args: argparse.Namespace) -> int:
    """operation key から、それを含む MSG ID 一覧を出力する。"""

    operation = OperationKey.from_storage(
        args.rotation,
        args.translation,
        args.time_reversal,
    )
    msg_ids = find_msg_ids_by_operation(args.db, operation)

    if args.format == "json":
        print(json.dumps({"msg_ids": msg_ids}, ensure_ascii=False))
    else:
        for msg_id in msg_ids:
            print(msg_id)
    return 0


def _query_metadata(args: argparse.Namespace) -> int:
    """生成 DB に保存した metadata を出力する。"""

    metadata = get_database_metadata(args.db)
    if args.format == "json":
        print(json.dumps(metadata, ensure_ascii=False))
    else:
        for key, value in metadata.items():
            print(f"{key}\t{value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
