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


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """None の default は表示せず、意味のある default だけ help に出す。"""

    def _get_help_string(self, action: argparse.Action) -> str:
        if action.default is None or action.default is argparse.SUPPRESS:
            return action.help or ""
        return super()._get_help_string(action) or ""


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

    parser = argparse.ArgumentParser(
        prog="msg-database",
        description="Build and query a SQLite database of magnetic space group data.",
        formatter_class=HelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest="command",
        metavar="{build,msg,operation,metadata}",
    )

    build = subparsers.add_parser(
        "build",
        help="build a SQLite database",
        description="Build a SQLite database from spglib MSG data.",
        formatter_class=HelpFormatter,
    )
    build.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        metavar="PATH",
        help="output SQLite database path",
    )
    build.add_argument(
        "--msg-id",
        type=int,
        action="append",
        metavar="MSG_ID",
        help=(
            "MSG ID to include as an integer in the range 1-1651; repeat this "
            "option to build a subset. When omitted, all MSG IDs are included"
        ),
    )

    msg = subparsers.add_parser(
        "msg",
        help="list operations for one MSG ID",
        description="List MSG type metadata and operation keys for one MSG ID.",
        formatter_class=HelpFormatter,
    )
    msg.add_argument(
        "msg_id",
        type=int,
        metavar="MSG_ID",
        help="MSG ID as an integer in the range 1-1651",
    )
    msg.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        metavar="PATH",
        help="input SQLite database path",
    )
    msg.add_argument(
        "--format",
        choices=["json", "table"],
        default="table",
        metavar="{json,table}",
        help="output format",
    )

    operation = subparsers.add_parser(
        "operation",
        help="list MSG IDs containing an operation key",
        description="List MSG IDs that contain one normalized operation key.",
        formatter_class=HelpFormatter,
    )
    operation.add_argument(
        "--rotation",
        required=True,
        metavar="R11,R12,...,R33",
        help=(
            "9 comma-separated integer rotation entries in row-major order, "
            "for example 1,0,0,0,1,0,0,0,1"
        ),
    )
    operation.add_argument(
        "--translation",
        required=True,
        metavar="T1,T2,T3",
        help=(
            "3 comma-separated translation entries as integers or fractions, "
            "for example 0,1/2,0"
        ),
    )
    operation.add_argument(
        "--time-reversal",
        type=int,
        choices=[0, 1],
        required=True,
        metavar="{0,1}",
        help="time-reversal flag: 0 for false, 1 for true",
    )
    operation.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        metavar="PATH",
        help="input SQLite database path",
    )
    operation.add_argument(
        "--format",
        choices=["json", "table"],
        default="table",
        metavar="{json,table}",
        help="output format",
    )

    metadata = subparsers.add_parser(
        "metadata",
        help="show database metadata",
        description="Show reproducibility metadata stored in the SQLite database.",
        formatter_class=HelpFormatter,
    )
    metadata.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        metavar="PATH",
        help="input SQLite database path",
    )
    metadata.add_argument(
        "--format",
        choices=["json", "table"],
        default="table",
        metavar="{json,table}",
        help="output format",
    )

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
